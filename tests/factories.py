# Third party
import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

# Local
from src.models import Librarian, Reader, Book
from src.api.auth import hash_password

####################################################################################################
# SETTINGS
####################################################################################################

fake = Faker()

####################################################################################################
# FACTORIES
####################################################################################################

class LibrarianFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Librarian
        sqlalchemy_session = None

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    password = factory.LazyAttribute(lambda _: hash_password(fake.password(length=12)))


class ReaderFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Reader
        sqlalchemy_session = None

    full_name = factory.LazyAttribute(lambda _: fake.name())
    email = factory.LazyAttribute(lambda _: fake.unique.email())


class BookFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Book
        sqlalchemy_session = None

    title = factory.LazyAttribute(lambda _: fake.sentence(nb_words=3))
    author = factory.LazyAttribute(lambda _: fake.name())
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    published_year = factory.LazyAttribute(lambda _: fake.year())
    isbn = factory.LazyAttribute(lambda _: fake.unique.isbn13(separator=""))
    quantity = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=10))
