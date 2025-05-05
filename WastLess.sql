CREATE DATABASE wasteless;
USE  wasteless;

-- 1) USERS
CREATE TABLE users (
  user_id        SERIAL PRIMARY KEY,
  email          VARCHAR(255) UNIQUE NOT NULL,
  password_hash  VARCHAR(255) NOT NULL,
  name           VARCHAR(100),
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2) FRIDGES
CREATE TABLE fridges (
  fridge_id      SERIAL PRIMARY KEY,
  name           VARCHAR(100) NOT NULL,
  location_desc  TEXT,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) LINK USERS ↔ FRIDGES (many-to-many for sharing)
CREATE TABLE fridge_users (
  fridge_id      INTEGER NOT NULL REFERENCES fridges(fridge_id) ON DELETE CASCADE,
  user_id        INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  role           VARCHAR(20) NOT NULL  -- e.g. 'owner', 'editor', 'viewer'
  , PRIMARY KEY(fridge_id, user_id)
);

-- 4) PRODUCTS (catalog of known foods)
CREATE TABLE products (
  product_id           SERIAL PRIMARY KEY,
  name                 VARCHAR(255) NOT NULL,
  category             VARCHAR(100),
  default_shelf_life   INT NOT NULL,  -- e.g. '14 days'
  default_open_life    INT            -- e.g. '3 days' once opened
);

-- 5) QRCODES → PRODUCT MAPPING
CREATE TABLE qr_codes (
  qr_code        VARCHAR(100) PRIMARY KEY,  -- the scanned code text
  product_id     INTEGER NOT NULL REFERENCES products(product_id),
  batch_info     VARCHAR(255),             -- optional batch/lot
  info_url       TEXT
);

-- 6) FRIDGE ITEMS (instances in a fridge)
CREATE TABLE fridge_items (
  item_id            SERIAL PRIMARY KEY,
  fridge_id          INTEGER NOT NULL REFERENCES fridges(fridge_id) ON DELETE CASCADE,
  added_by           INTEGER NOT NULL REFERENCES users(user_id),
  qr_code            VARCHAR(100) NOT NULL REFERENCES qr_codes(qr_code),
  added_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  factory_expires_at DATE NOT NULL,       -- from QR lookup
  opened_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP NULL,  -- null until user marks it “opened”

  -- computed spoil_date: opened_at + open_life_days (if opened),
  -- otherwise factory_expires_at
  open_life_days     INT NOT NULL,
  spoil_date         DATE AS (
                        CASE
                          WHEN opened_at IS NOT NULL
                            THEN DATE_ADD(opened_at, INTERVAL open_life_days DAY)
                          ELSE factory_expires_at
                        END
                      ) STORED
);

-- 7) NOTIFICATIONS
CREATE TABLE notifications (
  note_id            SERIAL PRIMARY KEY,
  item_id            INTEGER NOT NULL REFERENCES fridge_items(item_id) ON DELETE CASCADE,
  user_id            INTEGER NOT NULL REFERENCES users(user_id),
  notified_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  type               VARCHAR(20) NOT NULL,  -- e.g. 'about_to_spoil', 'spoiled'
  sent               BOOLEAN DEFAULT FALSE
);


-- Sample data for testing

-- 1) PRODUCTS & QR CODES
INSERT INTO products (name, category, default_shelf_life, default_open_life) VALUES
  ('Milk',            'Dairy'   ,   7,  3),
  ('Eggs',            'Dairy'   ,  21,  7),
  ('Butter',          'Dairy'   ,  90, 14),
  ('Cheese',          'Dairy'   ,  30,  7),
  ('Lettuce',         'Produce' ,   7,  3),
  ('Carrot',          'Produce' ,  14,  7),
  ('Yogurt',          'Dairy'   ,  14,  5),
  ('Chicken Breast',  'Meat'    ,   3,  2),
  ('Orange Juice',    'Beverage',  14,  5),
  ('Apple',           'Produce' ,  30, 14),
  ('Ham',             'Meat'    ,  14,  7),
  ('Tomato',          'Produce' ,  10,  5),
  ('Cucumber',        'Produce' ,  14,  7),
  ('Spinach',         'Produce' ,   7,  3),
  ('Beef Steak',      'Meat'    ,   5,  2)
;

INSERT INTO qr_codes (qr_code, product_id) VALUES
  ('QR001', 1),  ('QR002', 2),  ('QR003', 3),  ('QR004', 4),  ('QR005', 5),
  ('QR006', 6),  ('QR007', 7),  ('QR008', 8),  ('QR009', 9),  ('QR010',10),
  ('QR011',11),  ('QR012',12),  ('QR013',13),  ('QR014',14),  ('QR015',15)
;

-- 2) USERS
INSERT INTO users (email, password_hash, name) VALUES
  ('alice.@gmail.com', 'Abu2nsfj', 'Alice'),
  ('bob@gmail.com',   'kmroioiv', 'Bob'),
  ('carol@yhoo.com', 'Bojcrun232', 'Carol'),
  ('davoo@gmail.com',  'Bigdave', 'Dave')
;

-- 3) FRIDGES
INSERT INTO fridges (name, location_desc) VALUES
  ('Main Kitchen Fridge',  'Home, ground floor'),
  ('Garage Fridge',        'Home, garage'),
  ('Office Fridge',        'Workplace, 2nd floor'),
  ('Spare Fridge',         'Basement storage')
;

-- 4) FRIDGE ⟷ USER LINKS
INSERT INTO fridge_users (fridge_id, user_id, role) VALUES
  (1, 1, 'owner'),
  (1, 2, 'editor'),
  (1, 3, 'viewer');

-- Dave(4) owns Fridges 2–4
INSERT INTO fridge_users (fridge_id, user_id, role) VALUES
  (2, 4, 'owner'),
  (3, 4, 'owner'),
  (4, 4, 'owner');

-- 5) FRIDGE ITEMS (30 total)
-- Fridge 1 (10 items), added by Alice (user_id=1)
INSERT INTO fridge_items
  (fridge_id, added_by, qr_code, factory_expires_at, opened_at, open_life_days)
VALUES
  (1, 1, 'QR001', '2025-05-12', NULL,  3),
  (1, 1, 'QR002', '2025-05-26', NULL,  7),
  (1, 1, 'QR005', '2025-05-11', '2025-05-03 08:00:00',  3),
  (1, 1, 'QR010','2025-06-04', NULL, 14),
  (1, 1, 'QR004', '2025-06-05', '2025-05-02 12:30:00',  7),
  (1, 1, 'QR003', '2025-08-03', NULL, 14),
  (1, 1, 'QR006', '2025-05-19', NULL,  7),
  (1, 1, 'QR007', '2025-05-19', '2025-05-04 09:15:00',  5),
  (1, 1, 'QR009', '2025-05-19', NULL,  5),
  (1, 1, 'QR008', '2025-05-08', '2025-05-04 18:00:00',  2)
;

-- Fridge 2 (7 items), added by Dave (4)
INSERT INTO fridge_items
  (fridge_id, added_by, qr_code, factory_expires_at, opened_at, open_life_days)
VALUES
  (2, 4, 'QR011', '2025-05-19', NULL,  7),
  (2, 4, 'QR012', '2025-05-15', '2025-05-03 14:00:00',  5),
  (2, 4, 'QR013', '2025-05-19', NULL,  7),
  (2, 4, 'QR014', '2025-05-12', NULL,  3),
  (2, 4, 'QR015', '2025-05-10', '2025-05-02 11:00:00',  2),
  (2, 4, 'QR001', '2025-05-14', '2025-05-04 07:30:00',  3),
  (2, 4, 'QR002', '2025-06-01', NULL,  7)
;

-- Fridge 3 (7 items), Dave (4)
INSERT INTO fridge_items
  (fridge_id, added_by, qr_code, factory_expires_at, opened_at, open_life_days)
VALUES
  (3, 4, 'QR003', '2025-09-01', NULL, 14),
  (3, 4, 'QR004', '2025-07-04', '2025-05-03 10:00:00',  7),
  (3, 4, 'QR005', '2025-05-11', NULL,  3),
  (3, 4, 'QR006', '2025-05-20', '2025-05-02 16:45:00',  7),
  (3, 4, 'QR007', '2025-05-23', NULL,  5),
  (3, 4, 'QR008', '2025-05-07', '2025-05-04 19:30:00',  2),
  (3, 4, 'QR009', '2025-05-15', NULL,  5)
;

-- Fridge 4 (6 items), Dave (4)
INSERT INTO fridge_items
  (fridge_id, added_by, qr_code, factory_expires_at, opened_at, open_life_days)
VALUES
  (4, 4, 'QR010','2025-06-04', NULL, 14),
  (4, 4, 'QR011','2025-05-18', '2025-05-03 13:00:00',  7),
  (4, 4, 'QR012','2025-05-16', NULL,  5),
  (4, 4, 'QR013','2025-05-20', '2025-05-04 09:00:00',  7),
  (4, 4, 'QR014','2025-05-13', NULL,  3),
  (4, 4, 'QR015','2025-05-11', '2025-05-02 08:30:00',  2)
;

-- Notifications for Fridge 1 (item_ids 1–10, users 1–3)
INSERT INTO notifications (item_id, user_id, type, notified_at, sent) VALUES
  -- Item 1 is about to spoil tomorrow → notify Alice, Bob, Carol
  (1, 1, 'about_to_spoil', '2025-05-04 08:00:00', FALSE),
  (1, 2, 'about_to_spoil', '2025-05-04 08:00:00', FALSE),
  (1, 3, 'about_to_spoil', '2025-05-04 08:00:00', FALSE),

  -- Item 8 has just spoiled today → notify Alice, Bob, Carol
  (8, 1, 'spoiled',        '2025-05-05 09:00:00', FALSE),
  (8, 2, 'spoiled',        '2025-05-05 09:00:00', FALSE),
  (8, 3, 'spoiled',        '2025-05-05 09:00:00', FALSE);

-- Notifications for Fridge 2 (item_ids 11–17, user 4)
INSERT INTO notifications (item_id, user_id, type, notified_at, sent) VALUES
  -- Item 11 is about to spoil → notify Dave
  (11, 4, 'about_to_spoil', '2025-05-04 10:30:00', FALSE),

  -- Item 12 has spoiled → notify Dave
  (12, 4, 'spoiled',        '2025-05-05 07:45:00', FALSE);

