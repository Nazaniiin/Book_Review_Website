import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Connect to database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # Import data
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, years in reader:
        db.execute("INSERT INTO books (isbn, title, author, years) VALUES (:isbn, :title, :author, :years)",
                    {"isbn": isbn, "title": title, "author": author, "years": years})
        print(f"Added book {title} from {author} published in {years}.")
    db.commit()

if __name__ == "__main__":
    main()
