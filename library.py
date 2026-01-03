from sqlalchemy import create_engine, Column, Integer, String,Date, ForeignKey,func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date, timedelta
Base= declarative_base()

class Book(Base):
    __tablename__="books"
    book_id= Column(Integer, primary_key=True)
    title = Column(String(200),  nullable=False )
    author=Column(String(200), nullable=False)
    available_copies= Column(Integer, default=1)
    borrowings= relationship("Borrowing", back_populates="book")

class Member(Base):
    __tablename__="members"
    member_id=Column(Integer, primary_key=True)
    name=Column(String(200), nullable=False)
    email=Column(String(200), nullable=False, unique=True)
    password=Column(String(200), nullable=False)

    borrowings=relationship("Borrowing", back_populates="member")

class Borrowing(Base):
    __tablename__="borrowing"
    borrow_id= Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey('members.member_id'))
    book_id= Column(Integer, ForeignKey('books.book_id'))
    borrow_date=Column(Date,default=date.today)
    due_date= Column(Date, default= lambda: date.today()+ timedelta(days=14))
    return_date= Column(Date)
    fine= Column(Integer, default=0)

    member=relationship("Member", back_populates="borrowings")
    book= relationship("Book" ,back_populates="borrowings")

engine = create_engine(
    "mysql+mysqlconnector://root:1234hello@localhost:3306/library",
    echo=True
)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Enter numbers only")

def signup():
    print("signup to library\n")
    name=input("Name: ")
    email=input("email: ")
    password= input("password: ")

    if session.query(Member).filter_by(email=email).first():
        print("Email already exists \n")
        return None
    member=Member(name=name, email=email, password=password)
    session.add(member)
    session.commit()
    print("account created\n")
    return member

def sign_in():
    print("sign in to library system")
    email=input("E-mail : ")
    password=input ("Password : ")
    member=session.query(Member).filter_by(
        email=email,
        password=password
    ).first()

    if not member:
        print("invalid credentials ,Try again..")
        return None
    print(f"welcome {member.name}")
    return member

def view_books():
    books= session.query(Book).all()
    print("\n available books\n")
    for b in books:
        print(f"{b.book_id} and {b.title} ({b.available_copies}) copies ")

def borrow_books(member):
    view_books()
    book_id= get_int("\n enter  book id to borrow : ")
    book= session.query(Book).filter_by(book_id=book_id).first()
    if not book or book.available_copies<1:
        print("this book is unvailable right now\n")
    borrowing=Borrowing(
        member_id=member.member_id,
        book_id=book.book_id
    )
    
    book.available_copies -= 1
    session.add(borrowing)
    session.commit()

    print(f"✅ Borrowed '{book.title}'")


def return_book(member):
    active = session.query(Borrowing).filter_by(member_id=member.member_id,return_date=None).all()

    if not active:
        print("\nno borrowed book\n")
        return 
    print("\nyou borrowed book\n")
    for b in active:
        print(f" {b.borrow_id}: {b.book.title}")
    
    borrow_id= get_int("Enter borrow id to return: ")
    borrowing= session.query(Borrowing).filter_by(
        member_id=Member.member_id,
        borrow_id=borrow_id
    ).first()

    if not borrowing:
        print("invalid selection ")
        return
    today=date.today()
    borrowing.return_date=today

    if today>borrowing.due_date:
        days=(today-borrowing.due_date).days
        borrowing.fine=days*5
        print(f"fine: ${borrowing.fine}")
    Book.available_copies+=1
    session.commit()
    print("you have successfully returned the book")


def popular_book():
    results= session.query(Book.title,
                           func.count(Borrowing.borrow_id)).join(Borrowing).group_by(Book.book_id).order_by(func.count(Borrowing.borrow_id).desc()).all()
    print("\npopular books:\n")
    for title , count in results:
        print(f"{title} : {count} ")



def user_menu(member):
    while True:
        print("""
1. View Books
2. Borrow Book
3. Return Book
4. Popular Books
5. Sign Out""")
        choice=get_int("choose: ")
        if choice==1:
            view_books()
        elif choice==2:
            borrow_books(member)
        elif choice==3:
            return_book(member)
        elif choice==4:
            popular_book()
        elif choice==5:
            print("signed out")
            break
        else:
            print("invalid option")
    

def auth_menu():

    while True:
                print("""
==== Library System ====
1. Sign Up
2. Sign In
3. Exit
""")
                choice= get_int("choose : ")
                if choice==1:
                    user=signup()
                    if user:
                     user_menu(user)

                elif choice==2:
                    user=sign_in()
                    if user:
                        user_menu(user)
                elif choice==3:
                    print("system closed ")
                    break
                else:
                    print("Invalid choice ")


auth_menu()