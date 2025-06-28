from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import requests
from routers import users, listings
from database import Base, engine, SessionLocal
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time as dtime
import os
from openai import OpenAI
from schemas import ChatMessage, ChatMessageCreate, CalendarSlotCreate, CalendarSlotOut, BookingCreate, BookingOut
from models import ChatMessage as ChatMessageModel
import requests as pyrequests
import models
import shutil
from dotenv import load_dotenv
import re
import logging
from fastapi import status

load_dotenv()

# Настройка логирования с выводом времени
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title="Современный сайт объявлений", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key="your_secret_key_2024")
templates = Jinja2Templates(directory="templates")

# Создаем папку для статических файлов
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(listings.router)

# --- DEPENDENCIES ---

def get_current_user(request: Request) -> Optional[dict]:
    """Получить текущего пользователя из сессии"""
    return request.session.get("user")

def require_auth(request: Request):
    """Проверить авторизацию пользователя"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=302, detail="Требуется авторизация")
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- AUTH ROUTES ---

@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    """Главная страница - приветствие и призыв к регистрации"""
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    resp = requests.post("http://localhost:8000/users/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        user = resp.json()
        request.session["user"] = user
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный email или пароль"})

@app.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register", response_class=HTMLResponse)
def register_post(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    resp = requests.post("http://localhost:8000/users/register", json={"name": name, "email": email, "password": password, "role": "user"})
    if resp.status_code == 200:
        user = resp.json()
        request.session["user"] = user
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "error": "Ошибка регистрации. Возможно, email уже занят."})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)

# --- PROTECTED ROUTES ---

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    """Главная страница после авторизации"""
    user = require_auth(request)
    listings = db.query(models.Listing).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "listings": listings, "user": user})

@app.get("/listings", response_class=HTMLResponse)
def listings_page(
    request: Request, 
    region: str = None, 
    price_min: int = None, 
    price_max: int = None,
    rooms: str = None,
    min_area: float = None,
    max_area: float = None,
    finish: str = None,
    db: Session = Depends(get_db)
):
    """Страница с объявлениями"""
    user = require_auth(request)
    
    # Строим запрос к базе данных
    query = db.query(models.Listing)
    
    if region:
        query = query.filter(models.Listing.region.ilike(f"%{region}%"))
    if price_min:
        query = query.filter(models.Listing.price >= price_min)
    if price_max:
        query = query.filter(models.Listing.price <= price_max)
    if rooms:
        query = query.filter(models.Listing.rooms.ilike(f"%{rooms}%"))
    if min_area:
        query = query.filter(models.Listing.area >= min_area)
    if max_area:
        query = query.filter(models.Listing.area <= max_area)
    if finish:
        query = query.filter(models.Listing.remont.ilike(f"%{finish}%"))
    
    listings = query.all()
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.get("/listing/{listing_id}", response_class=HTMLResponse)
def listing_detail(request: Request, listing_id: int, db: Session = Depends(get_db)):
    user = require_auth(request)
    item = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not item:
        return templates.TemplateResponse("listing.html", {"request": request, "item": None, "user": user, "error": "Объявление не найдено"})
    return templates.TemplateResponse("listing.html", {"request": request, "item": item, "user": user})

@app.get("/create", response_class=HTMLResponse)
def create_get(request: Request):
    """Страница создания объявления"""
    user = require_auth(request)
    return templates.TemplateResponse("create.html", {"request": request, "user": user, "error": None, "success": None})

@app.post("/create", response_class=HTMLResponse)
def create_post(
    request: Request,
    title: str = Form(...),
    price: int = Form(...),
    address: str = Form(...),
    description: str = Form(...),
    rooms: str = Form(...),
    area: float = Form(...),
    living_area: float = Form(...),
    floor: str = Form(...),
    ceiling_height: str = Form(...),
    bathroom: str = Form(...),
    windows: str = Form(...),
    finish: str = Form(...),
    sale_type: str = Form(...),
    balcony: str = Form(...),
    participation_type: str = Form(...),
    completion_date: str = Form(...),
    building_type: str = Form(...),
    floors_total: int = Form(...),
    passenger_lift: int = Form(...),
    cargo_lift: int = Form(...),
    yard: str = Form(...),
    parking: str = Form(...),
    db: Session = Depends(get_db)
):
    user = require_auth(request)
    new_listing = models.Listing(
        title=title,
        price=price,
        address=address,
        description=description,
        rooms=rooms,
        area=area,
        living_area=living_area,
        floor=floor,
        sanuzel=bathroom,
        balkon_lodjiya=balcony,
        remont=finish,
        kv_condition=sale_type,
        kv_rule=participation_type,
        kv_about=completion_date,
        kv_name=building_type,
        kitchen_area=0,
        floors_total=floors_total,
        passenger_lift=passenger_lift,
        cargo_lift=cargo_lift,
        kv_rayon=yard,
        other_zhku=parking,
        seller_id=user["id"],
        region="",
        kv_img="",
        kv_zastr="",
        kv_stoim=None,
        kv_adres="",
        po_schetchikam="",
        mebel="",
        tehnika="",
        internet_tv="",
        room_type="",
        zalog=0,
        komissiya=0
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return templates.TemplateResponse("create.html", {"request": request, "user": user, "error": None, "success": "Объявление успешно создано!"})

@app.get("/my", response_class=HTMLResponse)
def my_listings(request: Request, db: Session = Depends(get_db)):
    """Мои объявления"""
    user = require_auth(request)
    listings = db.query(models.Listing).filter(models.Listing.seller_id == user["id"]).all()
    return templates.TemplateResponse("my.html", {"request": request, "listings": listings, "user": user})

# --- API ENDPOINTS ---

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Сервер работает"}

@app.get("/api/listings/filter")
def filter_listings_api(
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    region: Optional[str] = None,
    address: Optional[str] = None,
    rooms: Optional[str] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    min_living_area: Optional[float] = None,
    max_living_area: Optional[float] = None,
    min_kitchen_area: Optional[float] = None,
    max_kitchen_area: Optional[float] = None,
    floor: Optional[str] = None,
    min_floor: Optional[int] = None,
    max_floor: Optional[int] = None,
    min_floors_total: Optional[int] = None,
    max_floors_total: Optional[int] = None,
    finish: Optional[str] = None,
    sale_type: Optional[str] = None,
    building_type: Optional[str] = None,
    bathroom: Optional[str] = None,
    balcony: Optional[str] = None,
    windows: Optional[str] = None,
    mebel: Optional[str] = None,
    tehnika: Optional[str] = None,
    internet_tv: Optional[str] = None,
    passenger_lift: Optional[int] = None,
    cargo_lift: Optional[int] = None,
    yard: Optional[str] = None,
    parking: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    """API для расширенной фильтрации объявлений"""
    from sqlalchemy import func, or_
    
    query = db.query(models.Listing)
    
    # Фильтрация по цене
    if min_price is not None:
        query = query.filter(models.Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Listing.price <= max_price)
    
    # Фильтрация по региону
    if region:
        query = query.filter(models.Listing.region.ilike(f"%{region}%"))
    
    # Фильтрация по адресу
    if address:
        query = query.filter(models.Listing.address.ilike(f"%{address}%"))
    
    # Фильтрация по количеству комнат
    if rooms:
        query = query.filter(models.Listing.rooms.ilike(f"%{rooms}%"))
    
    # Фильтрация по площади
    if min_area is not None:
        query = query.filter(models.Listing.area >= min_area)
    if max_area is not None:
        query = query.filter(models.Listing.area <= max_area)
    
    if min_living_area is not None:
        query = query.filter(models.Listing.living_area >= min_living_area)
    if max_living_area is not None:
        query = query.filter(models.Listing.living_area <= max_living_area)
    
    if min_kitchen_area is not None:
        query = query.filter(models.Listing.kitchen_area >= min_kitchen_area)
    if max_kitchen_area is not None:
        query = query.filter(models.Listing.kitchen_area <= max_kitchen_area)
    
    # Фильтрация по этажу
    if floor:
        query = query.filter(models.Listing.floor.ilike(f"%{floor}%"))
    
    # Фильтрация по количеству этажей в доме
    if min_floors_total is not None:
        query = query.filter(models.Listing.floors_total >= min_floors_total)
    if max_floors_total is not None:
        query = query.filter(models.Listing.floors_total <= max_floors_total)
    
    # Фильтрация по отделке и состоянию
    if finish:
        query = query.filter(models.Listing.remont.ilike(f"%{finish}%"))
    if sale_type:
        query = query.filter(models.Listing.kv_condition.ilike(f"%{sale_type}%"))
    if building_type:
        query = query.filter(models.Listing.kv_name.ilike(f"%{building_type}%"))
    
    # Фильтрация по удобствам
    if bathroom:
        query = query.filter(models.Listing.sanuzel.ilike(f"%{bathroom}%"))
    if balcony:
        query = query.filter(models.Listing.balkon_lodjiya.ilike(f"%{balcony}%"))
    if windows:
        query = query.filter(models.Listing.windows.ilike(f"%{windows}%"))
    if mebel:
        query = query.filter(models.Listing.mebel.ilike(f"%{mebel}%"))
    if tehnika:
        query = query.filter(models.Listing.tehnika.ilike(f"%{tehnika}%"))
    if internet_tv:
        query = query.filter(models.Listing.internet_tv.ilike(f"%{internet_tv}%"))
    
    # Фильтрация по лифтам
    if passenger_lift is not None:
        query = query.filter(models.Listing.passenger_lift == passenger_lift)
    if cargo_lift is not None:
        query = query.filter(models.Listing.cargo_lift == cargo_lift)
    
    # Фильтрация по двору и парковке
    if yard:
        query = query.filter(models.Listing.kv_rayon.ilike(f"%{yard}%"))
    if parking:
        query = query.filter(models.Listing.other_zhku.ilike(f"%{parking}%"))
    
    # Сортировка
    if sort_by == "price":
        if sort_order == "asc":
            query = query.order_by(models.Listing.price.asc())
        else:
            query = query.order_by(models.Listing.price.desc())
    elif sort_by == "area":
        if sort_order == "asc":
            query = query.order_by(models.Listing.area.asc())
        else:
            query = query.order_by(models.Listing.area.desc())
    else:
        if sort_order == "asc":
            query = query.order_by(models.Listing.id.asc())
        else:
            query = query.order_by(models.Listing.id.desc())
    
    # Пагинация
    total = query.count()
    listings = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "listings": listings
    }

@app.get("/api/listings/search")
def search_listings_api(
    q: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """API для поиска объявлений по тексту"""
    from sqlalchemy import or_
    
    query = db.query(models.Listing).filter(
        or_(
            models.Listing.title.ilike(f"%{q}%"),
            models.Listing.description.ilike(f"%{q}%"),
            models.Listing.address.ilike(f"%{q}%"),
            models.Listing.region.ilike(f"%{q}%"),
            models.Listing.kv_name.ilike(f"%{q}%"),
            models.Listing.kv_rayon.ilike(f"%{q}%")
        )
    )
    
    total = query.count()
    listings = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "query": q,
        "listings": listings
    }

@app.get("/api/listings/stats")
def get_listings_stats_api(db: Session = Depends(get_db)):
    """API для получения статистики по объявлениям"""
    from sqlalchemy import func
    
    total_listings = db.query(models.Listing).count()
    
    # Статистика по ценам
    price_stats = db.query(
        func.min(models.Listing.price).label("min_price"),
        func.max(models.Listing.price).label("max_price"),
        func.avg(models.Listing.price).label("avg_price"),
        func.count(models.Listing.price).label("count")
    ).first()
    
    # Статистика по регионам
    region_stats = db.query(
        models.Listing.region,
        func.count(models.Listing.id).label("count")
    ).group_by(models.Listing.region).all()
    
    # Статистика по количеству комнат
    rooms_stats = db.query(
        models.Listing.rooms,
        func.count(models.Listing.id).label("count")
    ).group_by(models.Listing.rooms).all()
    
    return {
        "total_listings": total_listings,
        "price_stats": {
            "min_price": float(price_stats.min_price) if price_stats.min_price else 0,
            "max_price": float(price_stats.max_price) if price_stats.max_price else 0,
            "avg_price": float(price_stats.avg_price) if price_stats.avg_price else 0,
            "count": price_stats.count
        },
        "region_stats": [{"region": stat.region, "count": stat.count} for stat in region_stats if stat.region],
        "rooms_stats": [{"rooms": stat.rooms, "count": stat.count} for stat in rooms_stats if stat.rooms]
    }

# --- CHAT ROUTES ---

@app.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    user = require_auth(request)
    return templates.TemplateResponse("chat.html", {"request": request, "user": user})

@app.get("/api/chat/history")
def chat_history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    now = datetime.now()
    five_min_ago = now - timedelta(minutes=5)
    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.user_id == user["id"],
    ).order_by(ChatMessageModel.id).all()
    # Оставляем только сообщения за последние 5 минут
    messages = [m for m in messages if datetime.strptime(m.timestamp, "%Y-%m-%d %H:%M:%S") >= five_min_ago]
    return [ChatMessage.from_orm(m) for m in messages]

@app.post("/api/chat/send")
def chat_send(
    request: Request,
    data: ChatMessageCreate = Body(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Сохраняем сообщение пользователя
    msg = ChatMessageModel(
        user_id=user["id"],
        sender="user",
        message=data.message,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    # --- Улучшенная логика показа квартир в чате ---
    # Ключевые слова для фильтрации (тип, район, цена и т.д.)
    filter_keywords = ['студ', 'комнат', 'двуш', 'треш', 'четыр', 'район', 'центр', 'южн', 'север', 'цена', 'до', 'от', 'млн', 'тыс', 'руб', 'этаж', 'площадь', 'ремонт', 'мебел', 'техник', 'балкон', 'лоджия']
    # Если пользователь меняет фильтр — сбрасываем показанные id
    if any(word in data.message.lower() for word in filter_keywords):
        request.session['shown_listing_ids'] = []
    shown_ids = set(request.session.get('shown_listing_ids', []))
    more_keywords = ['ещё', 'остальные', 'следующ', 'показать ещё', 'more', 'next']
    all_keywords = ['все', 'весь список', 'показать все', 'all']
    show_all = any(word in data.message.lower() for word in all_keywords)
    show_more = any(word in data.message.lower() for word in more_keywords)
    # Определяем num (сколько квартир показывать за раз)
    num_map = {"одн": 1, "одну": 1, "одна": 1, "две": 2, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10}
    num = 5  # по умолчанию
    num_match = re.search(r'(\d+)', data.message.lower())
    if num_match:
        num = min(int(num_match.group(1)), 10)
    else:
        for word, val in num_map.items():
            if word in data.message.lower():
                num = val
                break
    # Фильтрация квартир (оставить умную фильтрацию как раньше)
    query = db.query(models.Listing)
    # ... (фильтры по параметрам) ...
    # Исключаем уже показанные, если не "все"
    if not show_all:
        query = query.filter(~models.Listing.id.in_(shown_ids))
    listings = query.order_by(models.Listing.price.asc()).limit(num).all()
    # Если ничего не найдено и это "ещё" — сообщаем, что всё показано
    if not listings and show_more:
        listings_text = "\nВсе подходящие квартиры уже были показаны. Если хотите рассмотреть другие варианты — уточните параметры поиска.\n"
    # Если пользователь просит "все" — показываем весь список без повторов
    elif show_all:
        listings = db.query(models.Listing).order_by(models.Listing.price.asc()).all()
        if listings:
            listings_text = f"\nВот все подходящие квартиры из базы (всего {len(listings)}):\n"
            for i, l in enumerate(listings, 1):
                listings_text += f"{i}) {l.title}, {l.address}, {l.area} м², {l.price} ₽, этаж: {l.floor}, район: {l.region}, ремонт: {l.remont}, мебель: {l.mebel}, техника: {l.tehnika}. {l.description}\n"
        else:
            listings_text = "\nВ базе пока нет квартир.\n"
        request.session['shown_listing_ids'] = [l.id for l in listings]
    # Обычная выдача (первые N новых)
    elif listings:
        session = request.session
        session['shown_listing_ids'] += [l.id for l in listings if l.id not in shown_ids]
        if len(listings) == 1:
            listings_text = "\nВот одна подходящая квартира из базы:\n"
        elif len(listings) == 2:
            listings_text = "\nВот две подходящие квартиры из базы:\n"
        elif len(listings) == 3:
            listings_text = "\nВот три подходящие квартиры из базы:\n"
        elif len(listings) == 4:
            listings_text = "\nВот четыре подходящие квартиры из базы:\n"
        elif len(listings) == 5:
            listings_text = "\nВот пять подходящих квартир из базы:\n"
        else:
            listings_text = f"\nВот {len(listings)} подходящих квартир из базы:\n"
        for i, l in enumerate(listings, 1):
            listings_text += f"{i}) {l.title}, {l.address}, {l.area} м², {l.price} ₽, этаж: {l.floor}, район: {l.region}, ремонт: {l.remont}, мебель: {l.mebel}, техника: {l.tehnika}. {l.description}\n"
    else:
        listings_text = "\nВ базе пока нет квартир.\n"
    # Получаем последние 5 сообщений пользователя и ИИ
    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.user_id == user["id"]
    ).order_by(ChatMessageModel.id.desc()).limit(5).all()
    messages = list(reversed(messages))  # чтобы были в хронологическом порядке
    # Формируем массив для YandexGPT, меняя 'ai' на 'assistant' и фильтруя пустые
    gpt_messages = [
        {"role": ("assistant" if m.sender == "ai" else m.sender), "text": m.message}
        for m in messages if m.message.strip()
    ]
    # Краткий и строгий system prompt
    system_prompt = (
        "Ты — эксперт по недвижимости в Краснодарском крае и Республике Адыгея. "
        "Используй только приведённые ниже квартиры из базы для ответа пользователю. "
        "Ни в коем случае не упоминай сторонние сайты, сервисы или источники. Не предлагай их. "
        "Если подходящих нет — честно скажи, что в базе нет вариантов. "
        "Отвечай официально, вежливо, экспертно-деловым языком, как представитель Ассоциации застройщиков."
    )
    listings_message = {
        "role": "assistant",
        "text": "Вот подходящие квартиры из базы:\n" + listings_text
    }
    gpt_messages = [{"role": "system", "text": system_prompt}, listings_message] + gpt_messages
    # Если вдруг истории нет — добавляем только system, варианты и текущее сообщение
    user_messages = [m for m in gpt_messages if m['role'] == 'user']
    if not user_messages:
        gpt_messages.append({"role": "user", "text": data.message})
    ai_text = "[Тестовый ответ YandexGPT: подключите IAM-токен]"
    IAM_TOKEN = os.getenv("YANDEXGPT_IAM_TOKEN")
    ENDPOINT = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    if IAM_TOKEN:
        try:
            headers = {
                "Authorization": f"Bearer {IAM_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "modelUri": "gpt://b1gafmlef4jlm4p2rpg8/yandexgpt-lite/latest",
                "completionOptions": {"stream": False, "temperature": 1.0, "maxTokens": 4000},
                "messages": gpt_messages
            }
            resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            ai_text = result["result"]["alternatives"][0]["message"]["text"].strip()
        except Exception as e:
            ai_text = f"[Ошибка YandexGPT: {e}]"
    # Сохраняем ответ AI с ролью 'ai' (для истории), но в prompt всегда будет 'assistant'
    ai_msg = ChatMessageModel(
        user_id=user["id"],
        sender="ai",
        message=ai_text,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    return {"user": ChatMessage.from_orm(msg), "ai": ChatMessage.from_orm(ai_msg)}

@app.get("/profile", response_class=HTMLResponse)
def profile_get(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    db_user = db.query(models.User).filter(models.User.id == user["id"]).first()
    return templates.TemplateResponse("profile.html", {"request": request, "user": db_user})

@app.post("/profile", response_class=HTMLResponse)
def profile_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    db_user = db.query(models.User).filter(models.User.id == user["id"]).first()
    db_user.name = name
    db_user.email = email
    db_user.phone = phone
    db.commit()
    db.refresh(db_user)
    return templates.TemplateResponse("profile.html", {"request": request, "user": db_user, "success": "Профиль обновлён!"})

print('YANDEXGPT_IAM_TOKEN:', os.getenv('YANDEXGPT_IAM_TOKEN'))

# --- КАЛЕНДАРЬ И БРОНИРОВАНИЕ ---

@app.get("/api/listing/{listing_id}/calendar", response_model=list[CalendarSlotOut])
def get_calendar_slots(listing_id: int, db: Session = Depends(get_db)):
    # Автоматическая генерация слотов на 2 недели вперёд, если их нет
    today = datetime.now().date()
    end_date = today + timedelta(days=14)
    slot_times = [dtime(9,0), dtime(10,30), dtime(12,0), dtime(13,30), dtime(15,0), dtime(16,30), dtime(18,0)]
    existing = db.query(models.CalendarSlot).filter(models.CalendarSlot.listing_id == listing_id, models.CalendarSlot.date >= str(today)).all()
    if not existing:
        slots = []
        for i in range(15):
            day = today + timedelta(days=i)
            for t in slot_times:
                slot = models.CalendarSlot(
                    listing_id=listing_id,
                    date=str(day),
                    time=t.strftime('%H:%M'),
                    is_booked=False
                )
                slots.append(slot)
        db.add_all(slots)
        db.commit()
    slots = db.query(models.CalendarSlot).filter(models.CalendarSlot.listing_id == listing_id, models.CalendarSlot.date >= str(today)).all()
    return slots

@app.post("/api/listing/{listing_id}/calendar", response_model=CalendarSlotOut, status_code=status.HTTP_201_CREATED)
def create_calendar_slot(listing_id: int, slot: CalendarSlotCreate, db: Session = Depends(get_db)):
    db_slot = models.CalendarSlot(**slot.dict(), listing_id=listing_id)
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@app.post("/api/listing/{listing_id}/book", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def book_slot(listing_id: int, slot_id: int = Form(...), db: Session = Depends(get_db), request: Request = None):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    slot = db.query(models.CalendarSlot).filter(models.CalendarSlot.id == slot_id, models.CalendarSlot.listing_id == listing_id, models.CalendarSlot.is_booked == False).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Слот не найден или уже забронирован")
    slot.is_booked = True
    db.commit()
    booking = models.Booking(user_id=user["id"], listing_id=listing_id, slot_id=slot_id, created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
