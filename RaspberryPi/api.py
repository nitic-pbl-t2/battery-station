import requests

url = "https://mobazy.vercel.app/api/station/open"
# url = "http://localhost:3000/api/station/open"

try:
    response = requests.get(url)
    response.raise_for_status()  # エラーがあれば例外を発生させる

    data = response.json()

    # JSONデータからisOpenを取り出す
    isOpen = data.get("isOpen")

    if isOpen is not None:
        print("isOpen:", isOpen)
    else:
        print("isOpenが見つかりませんでした。")

except requests.exceptions.RequestException as e:
    print("APIへのリクエスト中にエラーが発生しました:", e)
except ValueError as e:
    print("JSONデータの解析中にエラーが発生しました:", e)


    