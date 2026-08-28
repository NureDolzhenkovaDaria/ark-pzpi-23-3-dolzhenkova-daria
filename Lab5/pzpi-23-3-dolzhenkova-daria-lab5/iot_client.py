import time
import requests

SERVER_URL = "http://127.0.0.1:8000/api/v1"
DEVICE_ID = "EMO_TERMINAL_01"
HEADERS = {"x-role": "admin"}

def get_ad_id_by_emotion(emotion: str):
    try:
        res = requests.get(f"{SERVER_URL}/admin/ads", headers=HEADERS, timeout=3)
        if res.status_code == 200:
            for ad in res.json():
                if ad.get("emotion", "").lower() == emotion.lower():
                    return ad.get("id")
    except Exception:
        pass
    emotion_map = {'happy': 1, 'sad': 2, 'tired': 3, 'angry': 4}
    return emotion_map.get(emotion.lower(), 1)

def send_emotion_request(emotion: str):
    print(f"\n[{DEVICE_ID}] Статус змінено на: Locked (Обробка вибору емоції...)")
    payload = {"emotion": emotion.strip().lower()}
    
    try:
        response = requests.post(f"{SERVER_URL}/get_ad", json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            target_ad_id = data.get("id") or data.get("ad_id") or get_ad_id_by_emotion(emotion)
            
            print(f"[УСПІХ] Сервер повернув промокод: {data.get('promo_code')}")
            print(f"[РЕКЛАМА] {data.get('slogan')}")
            
            ans = input("Бажаєте оцінити цю рекламу? (y/n): ").strip().lower()
            if ans == 'y':
                try:
                    rating = int(input("Введіть оцінку (1-5): "))
                    if 1 <= rating <= 5:
                        comment = input("Ваш коментар (необов'язково): ")
                        fb_payload = {
                            "user_id": 1,
                            "ad_id": target_ad_id,
                            "rating": rating,
                            "comment": comment
                        }
                        res = requests.post(f"{SERVER_URL}/user/feedback", json=fb_payload)
                        if res.status_code == 201:
                            print("[ДЯКУЄМО] Відгук збережено!")
                        else:
                            print(f"[ПОМИЛКА {res.status_code}] Не вдалося зберегти відгук.")
                    else:
                        print("[ПОМИЛКА] Оцінка має бути від 1 до 5.")
                except ValueError:
                    print("[ПОМИЛКА] Потрібно ввести ціле число.")
                    
        elif response.status_code == 404:
            print(f"[ПОМИЛКА 404] Рекламу для емоції '{emotion}' не знайдено.")
        else:
            print(f"[ПОМИЛКА {response.status_code}] Відповідь: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[ПОМИЛКА МЕРЕЖІ] {e}")
        
    finally:
        print(f"[{DEVICE_ID}] Статус повернено до: Draft. Готово до введення.\n")

def list_all_ads():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Список всієї реклами ---")
    try:
        res = requests.get(f"{SERVER_URL}/admin/ads", headers=HEADERS)
        if res.status_code == 200:
            ads = res.json()
            if not ads:
                print("База реклами порожня.")
            for ad in ads:
                print(f"ID: {ad['id']} | Емоція: {ad['emotion']} | Промокод: {ad['promo_code']} | Слоган: {ad['slogan']}")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Не вдалося завантажити список.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("---------------------------------------------------\n")

def add_new_ad():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Додавання реклами ---")
    emotion = input("Емоція: ").strip().lower()
    promo = input("Промокод: ").strip()
    slogan = input("Рекламний слоган: ").strip()
    
    payload = {"emotion": emotion, "promo_code": promo, "slogan": slogan}
    try:
        res = requests.post(f"{SERVER_URL}/admin/add_ad", json=payload, headers=HEADERS)
        if res.status_code == 201:
            data = res.json()
            print(f"[УСПІХ] Рекламу додано під ID: {data.get('id')}")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Помилка додавання.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("------------------------------------------------\n")

def edit_ad():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Редагування реклами ---")
    try:
        ad_id = int(input("Введіть ID реклами, яку хочете змінити: "))
        emotion = input("Нова емоція: ").strip().lower()
        promo = input("Новий промокод: ").strip()
        slogan = input("Новий слоган: ").strip()
        
        payload = {"emotion": emotion, "promo_code": promo, "slogan": slogan}
        res = requests.put(f"{SERVER_URL}/admin/edit_ad/{ad_id}", json=payload, headers=HEADERS)
        
        if res.status_code == 200:
            print(f"[УСПІХ] Рекламу ID {ad_id} успішно оновлено!")
        elif res.status_code == 404:
            print(f"[ПОМИЛКА 404] Рекламу з ID {ad_id} не знайдено.")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Не вдалося оновити.")
    except ValueError:
        print("[ПОМИЛКА] ID має бути числом.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("---------------------------------------------------\n")

def delete_ad():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Видалення реклами ---")
    try:
        ad_id = int(input("Введіть ID реклами для видалення: "))
        res = requests.delete(f"{SERVER_URL}/admin/delete_ad/{ad_id}", headers=HEADERS)
        
        if res.status_code == 200:
            print(f"[УСПІХ] Рекламу з ID {ad_id} успішно видалено!")
        elif res.status_code == 404:
            print(f"[ПОМИЛКА 404] Рекламу з таким ID не знайдено.")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Помилка видалення.")
    except ValueError:
        print("[ПОМИЛКА] ID має бути числом.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("-------------------------------------------------\n")

def get_admin_analytics():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Аналітика ---")
    try:
        res = requests.get(f"{SERVER_URL}/admin/analytics/summary", headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            print(f"Всього взаємодій: {data.get('total_interactions')}")
            print("Розподіл емоцій:")
            for emo, stats in data.get('emotion_distribution', {}).items():
                print(f" - {emo}: {stats['count']} разів ({stats['percentage']}%)")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Доступ заборонено.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("------------------------------------------\n")

def get_admin_performance():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Ефективність реклами ---")
    try:
        res = requests.get(f"{SERVER_URL}/admin/ads/performance", headers=HEADERS)
        if res.status_code == 200:
            for item in res.json():
                print(f"ID: {item['ad_id']} | Емоція: {item['emotion']} | Рейтинг: {item['average_rating']} ★ (Відгуків: {item['total_reviews']}) | Слоган: {item['slogan']}")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Не вдалося завантажити звіт.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("---------------------------------------------------\n")

def create_system_backup():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Експорт резервної копії ---")
    try:
        res = requests.get(f"{SERVER_URL}/admin/export/backup", headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            print(f"Час бекапу: {data.get('export_timestamp')}")
            print(f"Всього банерів: {data.get('advertisements_count')}")
            print(f"Всього логів кліків: {data.get('logs_count')}")
            print(f"Користувачів у системі: {data.get('users_count')}")
            print("[УСПІХ] Резервну копію згенеровано.")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Помилка створення бекапу.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("------------------------------------------------------\n")

def toggle_user_block():
    print("\n--- ПАНЕЛЬ АДМІНІСТРАТОРА: Блокування користувача ---")
    try:
        user_id = int(input("Введіть ID користувача для зміни статусу: "))
        res = requests.patch(f"{SERVER_URL}/admin/users/{user_id}/block", headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            print(f"[УСПІХ] {data.get('message')} (User ID: {data.get('user_id')}, Blocked: {data.get('is_blocked')})")
        else:
            print(f"[ПОМИЛКА {res.status_code}] Помилка виконання.")
    except ValueError:
        print("[ПОМИЛКА] ID має бути числом.")
    except Exception as e:
        print(f"Помилка: {e}")
    print("----------------------------------------------------\n")

def main():
    print(f"=== Інтерактивний Smart-термінал {DEVICE_ID} ===")
    print("--- Клієнтський вибір емоції ---")
    print(" 1. Happy")
    print(" 2. Sad")
    print(" 3. Tired")
    print(" 4. Angry")
    print("--- Адміністрування реклами ---")
    print(" 5. Список банерів (list)")
    print(" 6. Додати банер (add)")
    print(" 7. Редагувати банер (edit)")
    print(" 8. Видалити банер (del)")
    print("--- Аналітика та сервіс ---")
    print(" 9. Загальна аналітика (stats)")
    print(" 10. Рейтинг реклами (perf)")
    print(" 11. Резервна копія (backup)")
    print(" 12. Блокування користувача (block)")
    print(" 0. Вихід (exit)\n")
    
    while True:
        cmd = input("Оберіть дію (цифру або назву): ").strip().lower()
        if cmd in ['0', 'exit']:
            break
        elif cmd in ['1', 'happy']:
            send_emotion_request('happy')
        elif cmd in ['2', 'sad']:
            send_emotion_request('sad')
        elif cmd in ['3', 'tired']:
            send_emotion_request('tired')
        elif cmd in ['4', 'angry']:
            send_emotion_request('angry')
        elif cmd in ['5', 'list']:
            list_all_ads()
        elif cmd in ['6', 'add']:
            add_new_ad()
        elif cmd in ['7', 'edit']:
            edit_ad()
        elif cmd in ['8', 'del']:
            delete_ad()
        elif cmd in ['9', 'stats']:
            get_admin_analytics()
        elif cmd in ['10', 'perf']:
            get_admin_performance()
        elif cmd in ['11', 'backup']:
            create_system_backup()
        elif cmd in ['12', 'block']:
            toggle_user_block()
        elif cmd:
            send_emotion_request(cmd)

if __name__ == "__main__":
    main()