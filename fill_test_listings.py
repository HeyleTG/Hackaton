import random
from database import SessionLocal
import models

regions = ["Центральный", "Северный", "Южный", "Восточный", "Западный"]
addresses = [
    "ул. Ленина, д. 10", "ул. Гагарина, д. 5", "пр. Мира, д. 22", "ул. Победы, д. 7", "ул. Советская, д. 15",
    "ул. Уральская, д. 87/7", "ул. Пушкина, д. 1", "ул. Кирова, д. 12", "ул. Садовая, д. 3", "ул. Молодёжная, д. 8",
    "ул. Новая, д. 14", "ул. Парковая, д. 6", "ул. Школьная, д. 9", "ул. Спортивная, д. 11", "ул. Озёрная, д. 4",
    "ул. Лесная, д. 2", "ул. Полевая, д. 13", "ул. Заречная, д. 16", "ул. Центральная, д. 18", "ул. Южная, д. 20"
]
remont_types = ["евроремонт", "косметика", "без отделки", "дизайнерский", "требует ремонта"]
rooms_list = ["студия", "1", "2", "3", "4+"]
balkon_types = ["балкон", "лоджия", "нет"]
sanuzel_types = ["раздельный", "совмещённый"]

user_id = 1  # id пользователя-продавца (можно изменить на существующего)

listings_data = []
for i in range(20):
    region = random.choice(regions)
    address = addresses[i]
    rooms = random.choice(rooms_list)
    area = round(random.uniform(20, 120), 1)
    living_area = round(area * random.uniform(0.5, 0.8), 1)
    kitchen_area = round(area * random.uniform(0.15, 0.25), 1)
    floor = f"{random.randint(1, 25)} из {random.randint(5, 25)}"
    price = random.randint(1800000, 15000000)
    remont = random.choice(remont_types)
    balkon = random.choice(balkon_types)
    sanuzel = random.choice(sanuzel_types)
    title = f"Квартира {rooms}-комн., {area} м², {floor}"
    description = f"Просторная {rooms}-комнатная квартира с {remont}. Район: {region}."
    listing = models.Listing(
        title=title,
        price=price,
        address=address,
        description=description,
        rooms=rooms,
        area=area,
        living_area=living_area,
        floor=floor,
        ceiling_height="2.7 м",
        bathroom=sanuzel,
        windows="во двор",
        finish=remont,
        sale_type="продажа",
        balcony=balkon,
        participation_type="ДДУ",
        completion_date="2025",
        building_type="монолит",
        floors_total=int(floor.split(" из ")[-1]),
        passenger_lift=random.randint(0, 1),
        cargo_lift=random.randint(0, 1),
        yard="закрытый",
        parking="есть",
        seller_id=user_id,
        region=region,
        kv_img="",
        kv_zastr="",
        kv_stoim=price,
        kv_adres=address,
        kv_about="",
        kv_name="ЖК Тестовый",
        kitchen_area=kitchen_area,
        remont=remont,
        mebel="частично",
        tehnika="есть",
        internet_tv="есть",
        balkon_lodjiya=balkon,
        room_type=rooms,
        zalog=0,
        komissiya=0,
        po_schetchikam="есть",
        other_zhku="парковка"
    )
    listings_data.append(listing)

# Добавляем в базу
with SessionLocal() as db:
    for l in listings_data:
        db.add(l)
    db.commit()

print("✅ В базу добавлено 20 тестовых объявлений!") 