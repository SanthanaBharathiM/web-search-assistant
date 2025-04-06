import ollama
import requests
from bs4 import BeautifulSoup
import trafilatura

# System prompts
assistant_msg = {
    'role': 'system',
    'content': (
        'You are an AI assistant that has another AI model working to get you live data from search '
        'engine results that will be attached before a USER PROMPT. You must analyze the SEARCH RESULT'
        'and use any relevant data to generate the most useful & intelligent response an AI assistant '
        'that always impresses the user would generate.'
    )
}

search_or_not_msg = (
    'You are not an AI assistant. Your only task is to decide if the last user prompt in a conversation'
    'with an AI assistant requires more data to be retrieved from a searching Google for the assistant'
    'to respond correctly. The conversation may or may not already have exactly the context data needed.'
    'If the assistant should search google for more data before responding to ensure a correct response,'
    'simply respond "True". If the conversation already has the context, or a Google search is not what an'
    'intelligent human would do to respond correctly to the last message in the convo, respond "False".'
    'Do not generate any explanations. Only generate "True" or "False" as a response in this conversation'
    'using the logic in these instructions.'
)

query_msg = (
    'You are not an AI assistant that responds to a user. You are an AI web search query generator model.'
    'You will be given a prompt to an AI assistant with web search capabilities. If you are being used, an'
    'AI has determined this prompt to the actual AI assistant, requires web search for more recent data.'
    'You must determine what the data is the assistant needs from search and generate the best possible'
    'DuckDuckGo query to find that data. Do not respond with anything but a query that an expert human'
    'search engine user would type into DuckDuckGo to find the needed data. Keep your queries simple,'
    'without any search engine code. Just type a query likely to retrieve the data we need. '
)

best_search_msg = (
    'You are not an AI assistant that responds to a user. You are an AI model trained to select the best '
    'search result out of a list of ten results. The best search result is the link an expert human search '
    'engine user would click first to find the data to respond to a USER_PROMPT after searching DuckDuckGo '
    'for the SEARCH_QUERY. \nAll user messages you receive in this conversation will have the format of: \n'
    'SEARCH_RESULTS: [{},{},{}] \n'
    'USER_PROMPT: "this will be an actual prompt to a web search enabled AI assistant" \n'
    'SEARCH_QUERY: "search query ran to get the above 10 links" \n\n'
    'You must select the index from the 0 indexed SEARCH_RESULTS list and only respond with the index of '
    'the best search result to check for the data the AI assistant needs to respond. That means your responses'
    'to this conversation should always be 1 token, being and integer between 0-9.'
)

contains_data_msg = (
    'You are not an AI assistant that responds to a user. You are an AI model designed to analyze data scraped '
    'from a web pages text to assist an actual AI assistant in responding correctly with up to date information. '
    'Consider the USER_PROMPT that was sent to the actual AI assistant & analyze the web PAGE_TEXT to see if '
    'it does contain the data needed to construct an intelligent, correct response. This web PAGE_TEXT was'
    'retrieved from a search engine using the SEARCH_QUERY that is also attached to user messages in this '
    'conversation. All user messages in this conversation will have the format of: \n'
    'PAGE_TEXT: "entire page text from the best search result based off the search snippet." \n'
    'USER_PROMPT: "the prompt sent to an actual web search enabled AI assistant." \n'
    'SEARCH_QUERY: "the search query that was used to find data determined necessary for the assistant to'
    'respond correctly and usefully." \n'
    'You must determine whether the PAGE_TEXT actually contains reliable and necessary data for the AI assistant'
    'to respond. You only have two possible responses to user messages in this conversation: "True" or "False".'
    'You never generate more than one token and it is always either "True" or "False" with True indicating that '
    'page text does indeed contain the reliable data for the AI assistant to use as context to respond. Respond '
    '"False" if the PAGE_TEXT is not useful to answering the USER_PROMPT.'
)

# Initialize conversation
assistant_conv = [assistant_msg]

def search_or_not():
    """Determine whether a web search is needed for the current query"""
    sys_msg = search_or_not_msg
    response = ollama.chat(model='llama3.1', messages=[{'role': 'system', 'content': sys_msg}, assistant_conv[-1]])
    content = response['message']['content']
    print(f'SEARCH OR NOT RESULTS: {content}')
    return 'true' in content.lower()

def scrape_webpage(url):
    """Scrape and extract text content from a webpage"""
    try:
        downloaded = trafilatura.fetch_url(url=url)
        return trafilatura.extract(downloaded, include_formatting=True, include_links=True)
    except Exception as e:
        return None

def query_generator():
    """Generate a search query based on the user prompt"""
    sys_msg = query_msg
    query_msg_content = f'CREATE A SEARCH QUERY FOR THIS PROMPT: \n{assistant_conv[-1]["content"]}'
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': sys_msg}, 
        {'role': 'user', 'content': query_msg_content}
    ])
    return response['message']['content']

def duckduckgo_search(query):
    """Perform a search using DuckDuckGo and return results"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    url = f'https://html.duckduckgo.com/html/?q={query}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    for i, result in enumerate(soup.find_all('div', class_='result'), start=0):
        if i >= 10:
            break
        title_tag = result.find('a', class_='result__a')
        if not title_tag:
            continue
        link = title_tag['href']
        snippet_tag = result.find('a', class_='result__snippet')
        snippet = snippet_tag.text.strip() if snippet_tag else 'No description available'
        results.append({'id': i, 'link': link, 'search_description': snippet})
    
    return results

def best_search_result(s_results, query):
    """Select the best search result from the list"""
    sys_msg = best_search_msg
    best_msg = f'SEARCH_RESULTS: {s_results} \nUSER_PROMPT: {assistant_conv[-1]["content"]} \nSEARCH_QUERY: {query}'
    
    for _ in range(2):
        try:
            response = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': sys_msg}, 
                {'role': 'user', 'content': best_msg}
            ])
            return int(response['message']['content'])
        except:
            continue
    
    return 0

def contains_data_needed(search_content, query):
    """Determine if scraped content contains the data needed"""
    sys_msg = contains_data_msg
    needed_prompt = f'PAGE_TEXT: {search_content} \nUSER_PROMPT: {assistant_conv[-1]["content"]} \nSEARCH_QUERY: {query}'
    
    response = ollama.chat(model='llama3.1', messages=[
        {'role': 'system', 'content': sys_msg}, 
        {'role': 'user', 'content': needed_prompt}
    ])
    
    content = response['message']['content']
    return 'true' in content.lower()

def ai_search():
    """Perform the full search process to find relevant context"""
    context = None
    print('GENERATING SEARCH QUERY.')
    search_query = query_generator()
    
    if search_query[0] == '"':
        search_query = search_query[1:-1]
    
    search_result = duckduckgo_search(search_query)
    context_found = False
    
    while not context_found and len(search_result) > 0:
        best_result = best_search_result(s_results=search_result, query=search_query)
        
        try:
            page_link = search_result[best_result]['link']
        except:
            print('FAILED TO SELECT BEST SEARCH RESULT, TRYING AGAIN.')
            search_result.pop(0)  # Remove the first result and try again
            continue

        page_text = scrape_webpage(page_link)
        search_result.pop(best_result)
        
        if page_text and contains_data_needed(search_content=page_text, query=search_query):
            context = page_text
            context_found = True
    
    return context

def stream_assistant_response():
    """Stream the assistant's response to the console"""
    global assistant_conv
    response_stream = ollama.chat(model="llama3.1", messages=assistant_conv, stream=True)
    complete_response = ''

    print("ASSISTANT")

    for chunk in response_stream:
        chunk_content = chunk['message']['content']
        print(chunk_content, end='', flush=True)
        complete_response += chunk_content
    
    assistant_conv.append({"role": "assistant", 'content': complete_response})
    print('\n\n')

def main():
    """Main function to run the web search assistant"""
    global assistant_conv
    
    while True:
        prompt = input("USER\n")
        assistant_conv.append({"role": "user", "content": prompt})
        
        if search_or_not():
            print("Web search required")
            context = ai_search()
            assistant_conv = assistant_conv[:-1]  # Remove the last user message
            
            if context:
                prompt = f'SEARCH RESULT: {context} \n\nUSER PROMPT: {prompt}'
            else:
                prompt = (f'USER PROMPT: \n{prompt} \n\nFAILED SEARCH: \nThe '
                          'AI search model was unable to extract any reliable data. Explain that '
                          'and ask if the user would like you to search again or respond '
                          'without web search context. Do not respond if a search was needed '
                          'and you are getting this message with anything but the above request '
                          'of how the user would like to proceed')
            
            assistant_conv.append({'role': 'user', 'content': prompt})
        
        stream_assistant_response()

if __name__ == "__main__":
    main()
