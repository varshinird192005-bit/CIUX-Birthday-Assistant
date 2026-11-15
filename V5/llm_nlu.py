"""Optional OpenAI-powered semantic parser. The model parses language only; it never supplies facts."""
import os, json
def parse_with_llm(message):
    from openai import OpenAI
    client=OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    model=os.environ.get('OPENAI_MODEL','gpt-4.1-mini')
    instructions=("You are an NLU parser for a birthday lookup app. Return only JSON with keys intent and entities. "
      "Allowed intents: birthday_search,count_birthdays,upcoming_birthdays,person_place,unknown. "
      "Allowed entity keys: person_name,relationship,month,relative_date,relative_month. "
      "Never answer the factual question, never invent dates or people. If uncertain use unknown and empty entities.")
    response=client.responses.create(model=model,instructions=instructions,input=message)
    data=json.loads(response.output_text)
    if not isinstance(data,dict) or not isinstance(data.get('entities',{}),dict): raise ValueError('Invalid NLU JSON')
    allowed={'birthday_search','count_birthdays','upcoming_birthdays','person_place','unknown'}
    if data.get('intent') not in allowed: raise ValueError('Unsupported intent')
    allowed_entities={'person_name','relationship','month','relative_date','relative_month'}
    data['entities']={k:v for k,v in data.get('entities',{}).items() if k in allowed_entities}
    return data
