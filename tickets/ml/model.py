def predict_priority(text: str):
    # Normalize input text
    text = (text or '').lower()

    # High priority keywords (critical business / system impact)
    high_keywords = [
        'urgent', 'critical', 'payment failed', 'transaction failed',
        'not working', 'system down', 'server down', 'app crash',
        'crash', 'error', 'exception', 'data loss', 'data missing',
        'login failed', 'unable to login', 'security issue',
        'breach', 'unauthorized access', 'immediate', 'blocked',
        'production issue', 'outage'
    ]

    # Medium priority keywords (performance or partial impact)
    med_keywords = [
        'slow', 'timeout', 'delay', 'latency',
        'issue', 'bug', 'warning', 'intermittent',
        'performance issue', 'loading issue',
        'page not loading', 'minor issue'
    ]

    # Check high priority first
    for k in high_keywords:
        if k in text:
            return 'high', 0.95

    # Check medium priority
    for k in med_keywords:
        if k in text:
            return 'medium', 0.75

    # Default low priority
    return 'low', 0.6
