def enrich_with_context(parsed,state):
    e=parsed.setdefault('entities',{})
    for key in ('month','relationship'):
        if key not in e and state.get(key) is not None: e[key]=state[key]
    return parsed
def update_state(parsed,state):
    state=dict(state or {}); e=parsed.get('entities',{})
    for key in ('month','relationship','person_id','person_name'):
        if key in e: state[key]=e[key]
    return state
