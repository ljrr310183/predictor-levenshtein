# ============================================
# CONEXIÓN A BASE DE DATOS CON SQLite
# ============================================
# SQLite viene incluido en Python (no necesita pip install)
# JS:   mejor-sqlite3 o knex.js (npm install)
# PHP:  new PDO("sqlite:database.db")
# Java: jdbc:sqlite:database.db (JDBC driver)

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime


# ============================================
# 1. CONEXIÓN BÁSICA (forma funcional)
# ============================================

def connect_db(db_name="example.db"):
    """Crea conexión a SQLite y retorna conexión + cursor"""
    # PHP: $pdo = new PDO("sqlite:example.db")
    # JS:  const db = new Database("example.db")
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # resultados como diccionario en vez de tupla
    cursor = conn.cursor()
    return conn, cursor


def create_tables(cursor):
    """Crea las tablas si no existen"""
    # SQL puro — igual en todos los lenguajes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)


def insert_user(cursor, name, email, age):
    """Inserta un usuario con parámetros seguros (previene SQL Injection)"""
    # [!] NUNCA hagas esto: f"INSERT INTO users VALUES ('{name}')" <- SQL Injection
    # [+] Usa placeholders (?) para pasar valores de forma segura
    # PHP: $stmt->execute([$name, $email, $age])  (prepared statements)
    # JS:  db.prepare("INSERT INTO users...").run(name, email, age)
    cursor.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        (name, email, age)
    )
    return cursor.lastrowid


def get_all_users(cursor):
    """Obtiene todos los usuarios"""
    cursor.execute("SELECT * FROM users ORDER BY id")
    return cursor.fetchall()


def find_user_by_email(cursor, email):
    """Busca un usuario por email"""
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()  # una sola fila o None


def update_user(cursor, user_id, name=None, age=None):
    """Actualiza campos de un usuario"""
    if name:
        cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
    if age:
        cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, user_id))


def delete_user(cursor, user_id):
    """Elimina un usuario por ID"""
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))


# --- Demo funcional ---
print("=" * 50)
print("DEMO 1: Funciones básicas con SQLite")
print("=" * 50)

conn, cursor = connect_db("demo_funcional.db")
create_tables(cursor)

# Insertar usuarios
id1 = insert_user(cursor, "Carlos", "carlos@mail.com", 28)
id2 = insert_user(cursor, "Ana", "ana@mail.com", 25)
id3 = insert_user(cursor, "Luis", "luis@mail.com", 32)
conn.commit()  # [!] SIEMPRE hacer commit para guardar cambios

print(f"\nUsuarios insertados (IDs: {id1}, {id2}, {id3})")

# Listar todos
print("\n[*] Todos los usuarios:")
for user in get_all_users(cursor):
    print(f"  [{user['id']}] {user['name']} - {user['email']} (edad: {user['age']})")

# Buscar por email
found = find_user_by_email(cursor, "ana@mail.com")
if found:
    print(f"\n[>] Encontrado: {found['name']} ({found['email']})")

# Actualizar
update_user(cursor, id1, name="Carlos García", age=29)
conn.commit()

# Eliminar
delete_user(cursor, id3)
conn.commit()

print("\n[*] Después de actualizar y eliminar:")
for user in get_all_users(cursor):
    print(f"  [{user['id']}] {user['name']} - {user['email']} (edad: {user['age']})")

conn.close()


# ============================================
# 2. CONEXIÓN CON CLASES (Patrón Repository)
# ============================================
# El patrón Repository separa la lógica de BD de la lógica de negocio
# PHP: UserRepository extends Repository (Laravel Eloquent / Doctrine)
# Java: public interface UserRepository extends JpaRepository<User, Long>
# JS:  class UserRepository (TypeORM / Prisma)


@dataclass
class User:
    """Modelo de datos — representa un usuario en Python"""
    # PHP: class User extends Model (Eloquent)
    # Java: @Entity public class User { @Id Long id; }
    id: int = None
    name: str = ""
    email: str = ""
    age: int = 0
    created_at: str = ""

    def __str__(self):
        return f"User({self.id}, {self.name}, {self.email})"


@dataclass
class Post:
    """Modelo de datos — representa un post"""
    id: int = None
    user_id: int = 0
    title: str = ""
    content: str = ""
    created_at: str = ""


class Database:
    """Gestiona la conexión a SQLite (Singleton simplificado)"""
    # PHP: class Database { private static $instance; }
    # Java: @Configuration public class DatabaseConfig { @Bean DataSource ds() }

    def __init__(self, db_name="app.db"):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")  # activa foreign keys
        return self

    def close(self):
        if self.conn:
            self.conn.close()

    # Context manager: permite usar "with Database() as db:"
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()  # si hay error, deshace cambios
        else:
            self.conn.commit()    # si todo OK, guarda cambios
        self.close()
        return False


class UserRepository:
    """CRUD de usuarios — toda la lógica de BD vive aquí"""
    # PHP: class UserRepository { public function findAll(): Collection }
    # Java: public class UserRepository { public List<User> findAll() }

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                age INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def create(self, user: User) -> User:
        """Inserta un usuario y retorna el objeto con su ID"""
        self.cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            (user.name, user.email, user.age)
        )
        user.id = self.cursor.lastrowid
        return user

    def find_all(self) -> list[User]:
        """Retorna todos los usuarios como objetos User"""
        self.cursor.execute("SELECT * FROM users ORDER BY id")
        rows = self.cursor.fetchall()
        return [User(**dict(row)) for row in rows]

    def find_by_id(self, user_id: int) -> User | None:
        """Busca un usuario por ID"""
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        return User(**dict(row)) if row else None

    def find_by_email(self, email: str) -> User | None:
        """Busca un usuario por email"""
        self.cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = self.cursor.fetchone()
        return User(**dict(row)) if row else None

    def update(self, user: User) -> bool:
        """Actualiza un usuario existente"""
        self.cursor.execute(
            "UPDATE users SET name = ?, email = ?, age = ? WHERE id = ?",
            (user.name, user.email, user.age, user.id)
        )
        return self.cursor.rowcount > 0

    def delete(self, user_id: int) -> bool:
        """Elimina un usuario por ID"""
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return self.cursor.rowcount > 0

    def count(self) -> int:
        """Cuenta total de usuarios"""
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def search(self, query: str) -> list[User]:
        """Busca usuarios por nombre (LIKE)"""
        self.cursor.execute(
            "SELECT * FROM users WHERE name LIKE ?",
            (f"%{query}%",)
        )
        return [User(**dict(row)) for row in self.cursor.fetchall()]


class PostRepository:
    """CRUD de posts con relación a users"""

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

    def create(self, post: Post) -> Post:
        self.cursor.execute(
            "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
            (post.user_id, post.title, post.content)
        )
        post.id = self.cursor.lastrowid
        return post

    def find_by_user(self, user_id: int) -> list[Post]:
        """Obtiene todos los posts de un usuario"""
        self.cursor.execute(
            "SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return [Post(**dict(row)) for row in self.cursor.fetchall()]

    def find_with_author(self) -> list[dict]:
        """JOIN: obtiene posts con el nombre del autor"""
        # SQL JOIN — igual en todos los lenguajes
        # PHP (Eloquent): Post::with('user')->get()
        # JS (Prisma):    prisma.post.findMany({ include: { user: true } })
        self.cursor.execute("""
            SELECT posts.*, users.name as author_name
            FROM posts
            INNER JOIN users ON posts.user_id = users.id
            ORDER BY posts.created_at DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]


# --- Demo con clases ---
print("\n\n" + "=" * 50)
print("DEMO 2: Patrón Repository con clases")
print("=" * 50)

# "with" cierra la conexión automáticamente y hace commit/rollback
with Database("demo_clases.db") as db:
    users = UserRepository(db.conn)
    posts = PostRepository(db.conn)

    # Crear usuarios
    u1 = users.create(User(name="María", email="maria@mail.com", age=30))
    u2 = users.create(User(name="Pedro", email="pedro@mail.com", age=27))
    u3 = users.create(User(name="Sofía", email="sofia@mail.com", age=22))

    print(f"\n[+] Usuarios creados: {u1}, {u2}, {u3}")

    # Crear posts
    posts.create(Post(user_id=u1.id, title="Mi primer post", content="Hola mundo"))
    posts.create(Post(user_id=u1.id, title="Aprendiendo Python", content="SQLite es genial"))
    posts.create(Post(user_id=u2.id, title="Sobre bases de datos", content="SQL básico"))

    # Listar usuarios
    print("\n[*] Todos los usuarios:")
    for user in users.find_all():
        print(f"  {user}")

    # Buscar
    found = users.find_by_email("pedro@mail.com")
    print(f"\n[>] Buscado por email: {found}")

    # Actualizar
    found.name = "Pedro García"
    found.age = 28
    users.update(found)
    print(f"[~] Actualizado: {users.find_by_id(found.id)}")

    # Contar
    print(f"\n[#] Total usuarios: {users.count()}")

    # Buscar por nombre
    print(f"[>] Buscar 'Mar': {users.search('Mar')}")

    # Posts de un usuario
    print(f"\n[P] Posts de María:")
    for post in posts.find_by_user(u1.id):
        print(f"  - {post.title}: {post.content}")

    # JOIN: posts con autor
    print(f"\n[P] Todos los posts (con autor):")
    for post in posts.find_with_author():
        print(f"  - [{post['author_name']}] {post['title']}")

    # Eliminar usuario
    users.delete(u3.id)
    print(f"\n[-] Sofía eliminada. Quedan: {users.count()} usuarios")


# ============================================
# 3. MANEJO DE ERRORES CON BD
# ============================================

print("\n\n" + "=" * 50)
print("DEMO 3: Manejo de errores")
print("=" * 50)

# Ejemplo: intentar insertar email duplicado
try:
    with Database("demo_clases.db") as db:
        users = UserRepository(db.conn)
        users.create(User(name="María Clon", email="maria@mail.com", age=25))
except sqlite3.IntegrityError as e:
    # UNIQUE constraint failed
    print(f"[!] Error de integridad: {e}")
except sqlite3.OperationalError as e:
    # tabla no existe, SQL mal formado, etc
    print(f"[!] Error operacional: {e}")
except sqlite3.Error as e:
    # cualquier otro error de SQLite
    print(f"[!] Error de BD: {e}")


# ============================================
# 4. TRANSACCIONES (todo o nada)
# ============================================
# Una transacción agrupa operaciones:
# si UNA falla, se deshacen TODAS (rollback)
# PHP: DB::transaction(function() { ... })
# Java: @Transactional
# JS:  await prisma.$transaction([...])

print("\n\n" + "=" * 50)
print("DEMO 4: Transacciones")
print("=" * 50)

try:
    with Database("demo_clases.db") as db:
        users = UserRepository(db.conn)

        # esto debería funcionar
        users.create(User(name="Test1", email="test1@mail.com", age=20))

        # esto FALLA (email duplicado) → rollback de TODO
        users.create(User(name="Test2", email="maria@mail.com", age=21))

except sqlite3.IntegrityError:
    print("[!] Transaccion fallo -> rollback automatico (Test1 NO se guardo)")

# verificar que Test1 no se guardó
with Database("demo_clases.db") as db:
    users = UserRepository(db.conn)
    result = users.find_by_email("test1@mail.com")
    print(f"[>] Test1 existe? {'Si' if result else 'No'} -> Rollback funciono")
    print(f"[#] Total usuarios: {users.count()}")


# ============================================
# LIMPIEZA: eliminar archivos .db de ejemplo
# ============================================
import os

for db_file in ["demo_funcional.db", "demo_clases.db"]:
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"[x] {db_file} eliminado")
