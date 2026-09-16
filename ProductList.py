import os
import sqlite3


class ProductList:
    def __init__(self, db_name="MyProduct.db"):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
            """
        )
        self.connection.commit()

    def insert_product(self, product_id, product_name, product_price):
        self.connection.execute(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            (product_id, product_name, product_price),
        )
        self.connection.commit()

    def insert_products(self, products):
        self.connection.executemany(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            products,
        )
        self.connection.commit()

    def update_product(self, product_id, product_name=None, product_price=None):
        updates = []
        values = []

        if product_name is not None:
            updates.append("productName = ?")
            values.append(product_name)
        if product_price is not None:
            updates.append("productPrice = ?")
            values.append(product_price)

        if not updates:
            return False

        values.append(product_id)
        cursor = self.connection.execute(
            f"UPDATE Products SET {', '.join(updates)} WHERE productID = ?",
            values,
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_product(self, product_id):
        cursor = self.connection.execute(
            "DELETE FROM Products WHERE productID = ?",
            (product_id,),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def select_products(self, product_id=None):
        if product_id is None:
            cursor = self.connection.execute(
                "SELECT productID, productName, productPrice FROM Products ORDER BY productID"
            )
        else:
            cursor = self.connection.execute(
                "SELECT productID, productName, productPrice FROM Products WHERE productID = ?",
                (product_id,),
            )
        return [dict(row) for row in cursor.fetchall()]

    def insert_sample_products(self, count=1000):
        products = [
            (product_id, f"Electronic Product {product_id}", 10000 + product_id * 100)
            for product_id in range(1, count + 1)
        ]
        self.connection.executemany(
            """
            INSERT INTO Products (productID, productName, productPrice)
            VALUES (?, ?, ?)
            ON CONFLICT(productID) DO UPDATE SET
                productName = excluded.productName,
                productPrice = excluded.productPrice
            """,
            products,
        )
        self.connection.commit()

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    products = ProductList()
    products.insert_sample_products(1000)
    print(f"Total products: {len(products.select_products())}")
    print("Product 1:", products.select_products(1)[0])

    products.update_product(1, product_name="Updated Electronic Product", product_price=99900)
    print("Updated product 1:", products.select_products(1)[0])

    products.delete_product(1001)
    products.insert_product(1001, "Temporary Product", 50000)
    products.delete_product(1001)
    print("Temporary product exists:", bool(products.select_products(1001)))
    print("Total products after CRUD demo:", len(products.select_products()))
    products.close()