
def enrich_with_context(parsed, state):
    """
    Add previous conversation details when the current
    question does not provide those details.
    """

    entities = parsed.setdefault('entities', {})
    state = state or {}

    # Carry forward the previous month
    if 'month' not in entities and state.get('month') is not None:
        entities['month'] = state['month']

    # Carry forward the previous relationship
    if (
        'relationship' not in entities
        and state.get('relationship') is not None
    ):
        entities['relationship'] = state['relationship']

    # Carry forward the previous person when appropriate
    if (
        'person_id' not in entities
        and state.get('person_id') is not None
        and parsed.get('intent') == 'birthday_search'
    ):
        # Do not reuse a previous person for a new relationship query
        if 'relationship' not in entities:
            entities['person_id'] = state['person_id']
            entities['person_name'] = state.get('person_name')

    return parsed


def update_state(parsed, state, last_result_ids=None):
    """
    Save useful information from the current question
    for the next conversation turn.
    """

    state = dict(state or {})
    entities = parsed.get('entities', {})

    # Save month, relationship and person details
    for key in (
        'month',
        'relationship',
        'person_id',
        'person_name'
    ):
        if key in entities:
            state[key] = entities[key]

    # Save previous search result IDs when provided
    if last_result_ids is not None:
        state['last_result_ids'] = last_result_ids

    return state


def reset_state():
    """
    Return an empty conversation state.
    """
    return {}
