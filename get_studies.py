from mgnifyapi.utils import (
    config_loader,
    get_args,
    get_logger,
    assert_nonempty_keys,
    assert_nonempty_vals,
    normalize_url,
)

from mgnifyapi import get_study_results
from mgnifyapi import get_biome_info
import matplotlib.pyplot as plt

import os
import logging
import json

def resume_progress(
    outpath:str,
    study_file:str="mgnify_studies.json",
    analyses_file:str="mgnify_analyses.json",
    combo_info_file:str="df_studies_analyses.csv",
    logger: logging.Logger|None = None,
):
    # init
    start_at = 0

    if os.path.exists(os.path.join(outpath, study_file)):
        start_at = "download_study_info"
    if os.path.exists(os.path.join(outpath, analyses_file)):
        start_at = "download_analyses_info"
    if 

    return start_at



def download_list(
        config_filepath,
        biome_name,
        exp_name,
        out_dir,
        study_url,
        analysis_url,
        study_file:str="mgnify_studies.json",
        analysis_file:str="mgnify_analyses.json",
        logger: logging.Logger|None = None, 
):
    
    if logger:
        verbose = logger.info
    else:
        verbose = print

    # also resturns as a json
    verbose(f"Requesting studies to")
    study_info = get_biome_info.get_studies_info(
        biome_name = biome_name,
        outpath=out_dir,
        url=study_url,
        study_file=study_file,
    )
    # instead to df
    study_info = get_biome_info.studies_json_to_df(
        "output-test/mgnify_studies.json"
    )

def get_rag_response(
        config_filepath, 
        prompt, 
        logger: logging.Logger|None = None, 
        save_outputs:bool=False
    ):

    ## TODO PRECONDITION CHECKS
    # allow logging if ran as script
    if logger:
        verbose = logger.info
    else:
        verbose = print

    ## LOAD CONFIG PARAMETERS
    verbose(f"Path to config file: {config_filepath}")
    # load config params
    verbose("Loading config params ... ")
    config = config_loader(config_filepath)
    assert_nonempty_keys(config)
    assert_nonempty_vals(config)
    col_name = config["pubmed_rag"]["collection name"]
    llama_model = config["pubmed_rag"]["llama model"]
    llama_api = config["pubmed_rag"]["llama_api"]
    rag_out_path = config["pubmed_rag"]["rag output folder"]
    user = config["apoc_load_queries"]["neo4j"]["username"]
    pwd = config["apoc_load_queries"]["neo4j"]["password"]
    host = config["apoc_load_queries"]["neo4j"]["host"]
    bolt_port = config["apoc_load_queries"]["neo4j"]["bolt port"]
    http_port = config["apoc_load_queries"]["neo4j"]["http port"]
    verbose(f"Configuration: {config}")

    ## MAIN
    # get and check uris
    bolt_uri = normalize_url(host, bolt_port, scheme='bolt')
    http_uri = normalize_url(host, http_port)

    verbose(f"Searching question '{prompt}' in {col_name}")
    similar_vectors = find_similar_vectors(
        path_to_config=config_filepath, query=prompt, logger=logger
    )

    rag_pmids = get_pmids_from_rag(similar_vectors)
    verbose(f"Pubmed articles used for context: {rag_pmids}")

    verbose("Preparing llama role and task")
    role = """You are a LLM-RAG model with expertise on biological knowledge graphs (KGs). If the retrieved context does not provide useful information to answer the question, say that you do not know."""

    task = f"""
    Use the following pieces of information in the "Context" section to provide an answer to the "Question".
    Each context is annotated with a dictionary of metadata that includes: 
        1. "pmid" the pubmed ID of the Publication that the context is from.
        2. "KG" the name of the knowledge graph (KG) that is the focus of the publication.
    Please check the context information carefully and do not use information that is not relevant to the question. Your response must have a word count under 50.
    """

    # getting prompt
    llm_prompt = init_prompt(
        query=prompt, results=similar_vectors, role=role, task=task
    )

    # adding context from BKGR!!!
    verbose(f"Connecting to BKGR Neo4j database at {bolt_uri}...")
    # connect to neo4j instance
    connection = Neo4jConnection(user=user, pwd=pwd, uri=bolt_uri)
    # check connection
    assert isinstance(
        connection.neo4j_version, str
    ), f"Issue with Neo4j connection: {connection.neo4j_version}"

    verbose("Getting BKGR subgraph nodes and edges... ")
    # write cypher query
    cypher_query_pyvis = write_subgraph_cypher(
        connection=connection, pmids=rag_pmids, as_subgraph=False
    )
    verbose(cypher_query_pyvis)
    # run it
    subgraph = get_subgraph(connection=connection, cypher_query=cypher_query_pyvis)
    nodes, edges = parse_subgraph_cypher(subgraph)
    # getting kg names
    pmid_kg_mapping = annotate_with_kg(nodes, edges)
    # also annot with subg
    #subgraph_as_text = annotate_with_subgraph(nodes, edges)
    verbose("Adding KG name and subgraph (as text) metadata to LLM prompt")
    # annote
    for k, v in pmid_kg_mapping.items():
        llm_prompt[1]["content"] = llm_prompt[1]["content"].replace(k, v)
    # with subgraph
    # llm_prompt[1]["content"] += "Network:\n"
    # llm_prompt[1]["content"] += f'"{subgraph_as_text}"'

    verbose(f"Whole prompt length: {len(llm_prompt[0]['content'].split(' '))} {len(llm_prompt[1]['content'].split(' '))}")
    verbose(f"{llm_prompt}")
    # to the LLM
    llm_response = llama3(prompt=llm_prompt, model=llama_model, api=llama_api)
    # return response
    whole_response = f"""
    ### Question: 
    {prompt}
    
    ### Response: 
    {llm_response}
    
    #### Context given: 
    {list(pmid_kg_mapping.values())}
    """

    #verbose(whole_response)

    # GETTING VISUALISATIONS
    verbose("Getting BKGR subgraph in Neo4j... ")
    cypher_query_neo4j = write_subgraph_cypher(
        connection=connection, pmids=rag_pmids, as_subgraph=True
    )
    url = open_bkgr_subgraph_in_neo4j(
        connection=connection,
        cypher_query=cypher_query_neo4j,
        uri=http_uri,
        auto_open=False,
    )
    verbose(f"Neo4j subgraph URL: {url}")
    verbose("Complete.")
    connection.close()

    verbose(f"Creating subgraph in networkx..")
    nx_subgraph = create_nx_subgraph(nodes=nodes, edges=edges)

    # for check
    html_content = None
    # if want to output file
    if save_outputs:
        # create subgraph vis as html file
        pyvis_out = os.path.join(rag_out_path, "subgraph.html")
        verbose(f"Creating subgraph in pyvis. Saving to {pyvis_out}")
        create_subgraph_in_pyvis(
            nx_graph=nx_subgraph, 
            out_path=pyvis_out, 
            auto_open=True)
        # save llm response as md
        # Specify the file name
        file_name = "RAG_response.md"
        fully = os.path.join(rag_out_path, file_name)
        # Open the file in write mode and save the string
        with open(fully, "w") as file:
            file.write(whole_response)
        verbose(f"LLM response as .md saved to {fully}")

    else: 
        # get as html content?
        html_content = create_subgraph_in_pyvis(
            nx_graph=nx_subgraph, 
        )
        # check
        if html_content is None:
            raise AttributeError("Issue creating subgraph as html")

    return whole_response, html_content
    
if __name__ == "__main__":
    ## GET ARGS
    # init
    args = get_args(
        prog_name="get-mgnify-studies",
        others=dict(description="get studies from mgnify"),
    )
    config_filepath = args.config


    ## START LOG FILE
    logger = get_logger()
    logger.info(f"Arguments: {args}")

    llm_response, subgraph_html = get_rag_response(
        config_filepath,
        prompt,
        logger,
        save_outputs=True
    )

    print(llm_response, subgraph_html)

else:
    print("get_rag_answer... imported. Script not ran.")
