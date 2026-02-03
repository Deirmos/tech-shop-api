import os
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import AsyncClient
from unittest.mock import AsyncMock
from sqlalchemy import text

# Ensure required settings exist for tests before importing app/config.
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost/")
os.environ.setdefault("RABBITMQ_EMAIL_QUEUE", "email.order_confirmation")

from backend.services.email_service import email_service
from backend.core.config import settings
from backend.core.database import get_db, Base
from backend.services.user_service import user_service
from backend.main import app
from backend.schemas.user import UserRegister

from backend.models.product import Product

from backend.models.cart import CartItem

from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.core.utils.order_status_enums import OrderStatus

TEST_DATABASE_UTL = settings.TEST_DATABASE_URL

test_engine = create_async_engine(TEST_DATABASE_UTL, echo=True)

TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()

@pytest.fixture
async def db_session():
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session = TestSessionLocal(bind=connection)

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()

@pytest.fixture
def override_get_db(db_session):
    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def user_factory(db_session):
    async def create_user(
            email: str | None = None,
            password: str = "password123",
            username: str | None = None
    ):
        
        if not email:
            email = "testuser@example.com"

        if username is None:
            username = f"user_{email.split("@")[0]}"

        user_data = UserRegister(
            email=email,
            username=username,
            password=password
        )
        
        return await user_service.register_new_user(db_session, user_data)
    
    return create_user
    
@pytest.fixture
async def user(user_factory):
    return await user_factory()

@pytest.fixture
async def async_client(override_get_db):
    async with AsyncClient(
        app=app,
        base_url="https://test"
    ) as client:
        yield client

@pytest.fixture
async def auth_client(async_client, user):
    response = await async_client.post(
        "/api/user/login",
        data={
            "username": user.email,
            "password": "password123"
        }
    )

    token = response.json()["access_token"]
    async_client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return async_client

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    mock_send = AsyncMock()
    monkeypatch.setattr(email_service, "send_order_confirmation", mock_send)

    return mock_send

@pytest.fixture
def product_factory(db_session, category_factory):
    async def create_product(
            name: str = "Test Product",
            description: str = "Test Description",
            price: float = 100.0,
            stock: int = 10,
            category_id: int | None = None,
            is_delete: bool = False
    ):
        
        if category_id is None:
            default_category = await category_factory(name=f"Cat for {name}")
            category_id = default_category.id

        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            is_delete=is_delete,
            image_url="static/products/default.jpg"
        )

        db_session.add(product)
        
        await db_session.commit()
        await db_session.refresh(product)

        return product
    
    return create_product

@pytest.fixture
def category_factory(db_session):
    async def create_category(name="Default", slug=None):
        if slug is None:
            slug = name.lower().replace(" ", "-")

        from backend.models.category import Category

        category = Category(name=name, slug=slug)
        db_session.add(category)

        await db_session.commit()
        await db_session.refresh(category)

        return category
    
    return create_category

@pytest.fixture
def order_factory(db_session, user_factory, product_factory):
    async def _create_order(user=None, products_data=None, status=OrderStatus.NEW):
        """
        products_data: список кортежей [(product_obj, quantity), ...]
        """

        if user is None:
            user_obj = await user_factory()
            target_user_id = user_obj.id
        else:
            target_user_id = user.id if hasattr(user, "id") else user

        if products_data is None:
            product = await product_factory(name="Default Product", price=100, stock=10)
            products_data = [(product, 1)]

        total_price = sum(p.price * qty for p, qty in products_data)

        order = Order(
            user_id=target_user_id,
            total_price=total_price,
            status=status
        )

        db_session.add(order)
        await db_session.flush()

        for product, quantity in products_data:
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price
            )
            db_session.add(item)

        await db_session.commit()
        await db_session.refresh(order)
        
        return order

    return _create_order

@pytest.fixture
def cart_item_factory(db_session):
    async def _create_cart_item(
            user_id: int,
            product_id: int,
            quantity: int = 1
    ):
        
        actual_user_id = user_id.id if hasattr(user_id, "id") else user_id
        
        item = CartItem(user_id=actual_user_id, product_id=product_id, quantity=quantity)
        
        db_session.add(item)

        await db_session.commit()
        await db_session.refresh(item)

        return item
    
    return _create_cart_item

@pytest.fixture
async def admin_client(async_client, db_session, user_factory):
    admin = await user_factory(email="boss@test.com")
    admin.is_admin = True
    await db_session.commit()

    response = await async_client.post(
        "/api/user/login",
        data={"username": admin.email, "password": "password123"}
    )
    token = response.json()["access_token"]
    async_client.headers.update({"Authorization": f"Bearer {token}"})

    return async_client
