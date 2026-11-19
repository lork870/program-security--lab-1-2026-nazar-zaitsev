import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8080"
CLIENT_ID = "lily-05"
CLIENT_SECRET = "T2wL9eR6pA4h"


def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Accept": "application/json"}
    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


def main():
    print("1. Автоматична автентифікація (/auth/token)...")
    status, auth_data = make_request(
        "/auth/token",
        method="POST",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET},
    )
    if status != 200:
        print(f"Помилка автентифікації ({status}): {auth_data}")
        return

    token = auth_data.get("access_token")
    print(f"Токен отримано! (тип: {auth_data.get('token_type')}, діє: {auth_data.get('expires_in')} сек)\n")

    print("2. Поточний читач (/whoami):")
    _, whoami = make_request("/whoami", token=token)
    print(json.dumps(whoami, ensure_ascii=False, indent=2), "\n")

    print("3. Список книг (/api/books):")
    _, books_data = make_request("/api/books", token=token)
    print(json.dumps(books_data, ensure_ascii=False, indent=2), "\n")

    books_list = books_data.get("books") or books_data.get("items") or []
    if books_list and isinstance(books_list, list):
        first_id = books_list[0].get("id")
        if first_id:
            print(f"4. Деталі першої книги (/api/books/{first_id}):")
            _, book_detail = make_request(f"/api/books/{first_id}", token=token)
            print(json.dumps(book_detail, ensure_ascii=False, indent=2), "\n")

    print("5. Активні позики (/api/loans):")
    _, loans = make_request("/api/loans", token=token)
    print(json.dumps(loans, ensure_ascii=False, indent=2), "\n")

    print("6. Зведена інформація (/api/summary):")
    _, summary = make_request("/api/summary", token=token)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()