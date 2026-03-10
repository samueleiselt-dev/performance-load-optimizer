import requests


def build_strava_auth_url(client_id, redirect_uri):
    scope = "read,activity:read_all"

    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&approval_prompt=force"
        f"&scope={scope}"
    )

    return auth_url


def exchange_code_for_token(client_id, client_secret, code):
    token_url = "https://www.strava.com/oauth/token"

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code"
    }

    response = requests.post(token_url, data=payload)

    if response.status_code == 200:
        return response.json()

    return None


def fetch_activities(access_token, per_page=100, max_pages=5):
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}

    all_activities = []

    for page in range(1, max_pages + 1):
        params = {"per_page": per_page, "page": page}
        response = requests.get(activities_url, headers=headers, params=params)

        if response.status_code != 200:
            return None

        page_activities = response.json()

        if not page_activities:
            break

        all_activities.extend(page_activities)

    return all_activities