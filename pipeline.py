from agents import web_search_agent , scrape_url_agent , writer_chain , critics_chain

def run_pipeline_file(topic : str) -> dict:
    state = {}

    # Search agent is working
    print("\n" + " ="*50)
    print("Step - 1 : Search Agent is working")
    print("="*50)

    search_agent = web_search_agent()
    search_result = search_agent.invoke({
        "messages" : [{"role" : "user" , "content" : f"Finde recent relible , accurate information about : {topic}"}]
    })

    state['search_results'] = search_result['messages'][-1].content

    print("\n Search Content : \n", state['search_results'])


    # Scrape agent working

    print("\n" + " ="*50)
    print("Step - 2 : Scape url Agent is finding deep information")
    print("="*50)

    scrape_agent = scrape_url_agent()
    scrape_results = scrape_agent.invoke({
        "messages" : [{"role" : "user" , "content" : 
        f"Based on the following reseacrh results about the : '{topic}'\n"
        f"Pick the most relevant url and scrape for deeper content.\n\n"
        # i did not added [:800] after state['search_results]
        f"Search Results :\n {state['search_results']}"
            }]
    })

    state['scrape_results'] = scrape_results['messages'][-1].content

    print("\n Deeep scraped Content : \n", state['scrape_results'])

    # Step 3
    print("\n" + " ="*50)
    print("Step - 3 : Writer writting the report")
    print("="*50)

    reserch_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n "
        f"DEATILED SCRAPED CONTENT :  \n {state['scrape_results']}"
    )

    state['report'] = writer_chain.invoke({
        "topic" : topic,
        "research" : reserch_combined
    })

    print("\n Report : \n", state['report'])


    # step 4
    print("\n" + " ="*50)
    print("Step - 4 : Crics is reviwing the report")
    print("="*50)

    state['feedback'] = critics_chain.invoke({
        "report" : state['report']
    })

    print("\n Crtic  : \n", state['feedback'])

    return state


if __name__ =="__main__":
    topic = input("Enter the topic : ")
    run_pipeline_file(topic)
