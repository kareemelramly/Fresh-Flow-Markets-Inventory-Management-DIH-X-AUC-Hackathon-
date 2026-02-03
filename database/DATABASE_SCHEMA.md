# Fresh Flow Markets - Database Schema Documentation

## Overview

This document describes the complete database schema for the Fresh Flow Markets Inventory Management System. The database is designed to support:

1. **Inventory Management & Forecasting** - Track stock levels, predict demand, optimize prep quantities
2. **Menu Engineering** - Analyze menu performance, pricing optimization
3. **Operational Analytics** - Sales tracking, customer behavior, campaign performance
4. **Machine Learning Integration** - Data structured for training ML models for demand forecasting and inventory optimization

---

## Database Architecture

### Design Principles

- **Normalized Structure**: Dimension and fact tables following star schema pattern
- **Temporal Tracking**: All records include `created` and `updated` timestamps (UNIX format)
- **Soft Deletes**: `deleted` flag instead of hard deletes to preserve historical data
- **Multi-tenancy**: `place_id` for merchant isolation
- **Audit Trail**: `user_id` tracks who created/modified records

### Data Organization

```
📁 DATABASE
├── 📊 CORE ENTITIES (Dimension Tables)
│   ├── Products & Inventory
│   ├── Menu Management
│   ├── Locations & Users
│   └── Campaigns & Categories
│
├── 📈 TRANSACTIONAL DATA (Fact Tables)
│   ├── Orders & Sales
│   ├── Inventory Reports
│   ├── Financial Records
│   └── Campaign Performance
│
└── 📋 AGGREGATED VIEWS
    └── Pre-computed Analytics
```

---

## Table Categories

### 1. CORE ENTITIES (Dimension Tables)

These tables contain master data and reference information.

#### **A. Product & Inventory Management**

##### `dim_items` - Raw Inventory Items Catalog
**Purpose**: Master catalog of all raw ingredients, products, and inventory items

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update timestamp | UNIX timestamp |
| `accounting_reference` | INTEGER | External accounting system ID | For integration |
| `barcode` | VARCHAR | Product barcode | For scanning |
| `delivery` | BOOLEAN | Available for delivery | 1 = yes, 0 = no |
| `description` | TEXT | Item description | Full text description |
| `discountable` | BOOLEAN | Can be discounted | 1 = yes, 0 = no |
| `display_for_customers` | BOOLEAN | Show to customers | Customer-facing flag |
| `eat_in` | BOOLEAN | Available for eat-in | 1 = yes, 0 = no |
| `index` | INTEGER | Display order | For sorting |
| `number` | INTEGER | Item number | Internal reference |
| `price` | DECIMAL(10,2) | Base price | DKK currency |
| `purchases` | INTEGER | Total purchases count | Aggregated metric |
| `removable_ingredients` | TEXT | Removable components | JSON/comma-separated |
| `section_id` | INTEGER | Menu section ID | FK to sections |
| `status` | VARCHAR(20) | Item status | Active/Inactive |
| `takeaway` | BOOLEAN | Available for takeaway | 1 = yes, 0 = no |
| `title` | VARCHAR(255) | Item name | Display name |
| `trainee_mode` | BOOLEAN | Training mode flag | 0 = production |
| `type` | VARCHAR(50) | Item type | Normal/Special |
| `vat` | DECIMAL(5,2) | VAT percentage | Default: 25 |
| `add_on_category_ids` | TEXT | Add-on categories | Pipe-separated IDs |
| `printer_category_ids` | TEXT | Printer routing | For kitchen display |
| `standard_voucher_validity` | INTEGER | Voucher validity days | |
| `all_you_can_eat_validity` | INTEGER | AYCE validity | |

**Indexes:**
- PRIMARY: `id`
- INDEX: `section_id`, `status`, `user_id`
- FULLTEXT: `title`, `description`

**ML Usage**: Features for demand forecasting (price, section, historical purchases)

---

##### `dim_skus` - Stock Keeping Units
**Purpose**: Individual SKU records linking items to stock categories with inventory tracking

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | DATE | Creation date | YYYY-MM-DD |
| `updated` | DATE | Last update date | YYYY-MM-DD |
| `stock_category_id` | INTEGER | Stock category | FK to dim_stock_categories |
| `item_id` | DECIMAL | Reference item | FK to dim_items |
| `title` | VARCHAR(255) | SKU name | Display name |
| `quantity` | DECIMAL(10,2) | Current stock quantity | Updated in real-time |
| `low_stock_threshold` | DECIMAL(10,2) | Reorder point | Alert trigger |
| `type` | VARCHAR(50) | SKU type | normal/special |
| `unit` | VARCHAR(20) | Unit of measure | pcs/kg/liters |

**Indexes:**
- PRIMARY: `id`
- INDEX: `stock_category_id`, `item_id`, `quantity`
- UNIQUE: `stock_category_id` + `item_id`

**ML Usage**: Stock levels for inventory optimization, reorder prediction

---

##### `dim_stock_categories` - Inventory Categories
**Purpose**: Hierarchical organization of inventory items

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | DATE | Creation date | YYYY-MM-DD |
| `updated` | DATE | Last update date | YYYY-MM-DD |
| `place_id` | INTEGER | Merchant/location | FK to dim_places |
| `title` | VARCHAR(255) | Category name | e.g., "Kolde Drikke" |

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`

**ML Usage**: Categorization features for demand patterns

---

##### `dim_bill_of_materials` - Recipe Ingredients
**Purpose**: Links menu items to raw inventory with required quantities (BOM = Bill of Materials)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update timestamp | UNIX timestamp |
| `parent_sku_id` | INTEGER | Finished product SKU | FK to dim_skus |
| `sku_id` | INTEGER | Component SKU | FK to dim_skus |
| `quantity` | DECIMAL(10,3) | Required quantity | Per unit of parent |

**Indexes:**
- PRIMARY: `id`
- INDEX: `parent_sku_id`, `sku_id`
- COMPOSITE: `parent_sku_id` + `sku_id`

**ML Usage**: Calculate raw material needs from menu item sales forecasts

---

#### **B. Menu Management**

##### `dim_menu_items` - Menu Products
**Purpose**: The merchant's sellable menu catalog

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `section_id` | INTEGER | Menu section | FK to sections |
| `create` | DATETIME | Creation date | Human-readable |
| `title` | VARCHAR(255) | Item name | Display name |
| `type` | VARCHAR(50) | Item type | Normal/Special |
| `status` | VARCHAR(20) | Availability | Active/Inactive |
| `rating` | INTEGER | Average rating | 0-100 scale |
| `votes` | INTEGER | Number of ratings | Count |
| `purchases` | INTEGER | Total sold | Aggregated count |
| `price` | DECIMAL(10,2) | Selling price | DKK |
| `index` | INTEGER | Display order | For menu layout |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |

**Indexes:**
- PRIMARY: `id`
- INDEX: `section_id`, `status`, `purchases` DESC

**ML Usage**: Sales history for demand forecasting, price optimization

---

##### `dim_add_ons` - Product Add-ons/Modifiers
**Purpose**: Optional extras customers can add (toppings, sauces, sides)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | DATETIME | Creation date | Duplicate column |
| `updated` | DATETIME | Last update | Duplicate column |
| `category_id` | INTEGER | Add-on category | FK to categories |
| `deleted` | BOOLEAN | Soft delete flag | 0 = active |
| `demo_mode` | BOOLEAN | Demo flag | 0 = production |
| `index` | INTEGER | Display order | For sorting |
| `price` | DECIMAL(10,2) | Additional price | DKK |
| `select_as_default` | BOOLEAN | Auto-selected | 1 = default on |
| `status` | VARCHAR(20) | Availability | Active/Inactive |
| `title` | VARCHAR(255) | Add-on name | Display name |
| `created` (duplicate) | INTEGER | UNIX timestamp | |
| `updated` (duplicate) | INTEGER | UNIX timestamp | |

**Indexes:**
- PRIMARY: `id`
- INDEX: `category_id`, `status`, `deleted`

**ML Usage**: Popular combinations for recommendation engine

---

##### `dim_menu_item_add_ons` - Menu-to-Add-on Links
**Purpose**: Associates which add-ons are available for each menu item

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `category_id` | INTEGER | Add-on category | FK to categories |
| `create` | DATETIME | Creation date | Human-readable |
| `title` | VARCHAR(255) | Add-on name | Display name |
| `select_as_default` | BOOLEAN | Auto-selected | 1 = default |
| `status` | VARCHAR(20) | Availability | Active/Inactive |
| `index` | INTEGER | Display order | For sorting |
| `price` | DECIMAL(10,2) | Additional cost | DKK |
| `created` | INTEGER | UNIX timestamp | Audit |

**Indexes:**
- PRIMARY: `id`
- INDEX: `category_id`, `status`

---

#### **C. Locations & Users**

##### `dim_places` - Merchant/Location Master
**Purpose**: Central hub for all merchant locations (every table links here via place_id)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator/owner | FK to dim_users |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `title` | VARCHAR(255) | Merchant name | Business name |
| `activated` | BOOLEAN | Activation status | |
| `active` | BOOLEAN | Currently active | 1 = operational |
| `bankrupt` | BOOLEAN | Bankruptcy flag | 1 = yes |
| `binding_period` | INTEGER | Contract binding (months) | |
| `chain_id` | INTEGER | Chain membership | FK to chains |
| `contact_email` | VARCHAR(255) | Contact email | |
| `contact_mobile_phone` | VARCHAR(20) | Contact phone | |
| `contract_start` | INTEGER | Signup date | UNIX timestamp |
| `country` | VARCHAR(2) | Country code | ISO 2-letter |
| `currency` | VARCHAR(3) | Currency code | DKK/EUR/USD |
| `cvr_number` | VARCHAR(20) | Business reg number | Denmark CVR |
| `duplicate` | BOOLEAN | Duplicate account flag | Data quality |
| `ecommerce_fee` | DECIMAL(5,2) | E-commerce fee % | |
| `eu_commission` | DECIMAL(5,2) | EU commission % | |
| `invoicing_start_date` | INTEGER | Invoice start | UNIX timestamp |
| `isv_commission` | DECIMAL(5,2) | ISV partner commission % | |
| `isv_partner` | INTEGER | ISV partner ID | |
| `non_eu_commission` | DECIMAL(5,2) | Non-EU commission % | |
| `onboarded_by` | VARCHAR(100) | Onboarding source | |
| `payment_terminal_provider` | VARCHAR(100) | Terminal provider | |
| `area_id` | INTEGER | Geographic area | FK to taxonomy |
| `processing_fee` | DECIMAL(5,2) | Processing fee % | |
| `sales_outcome_id` | INTEGER | Sales outcome | FK to taxonomy |
| `sales_stage` | VARCHAR(50) | Sales pipeline stage | |
| `service_charge` | DECIMAL(5,2) | Service charge % | |
| `setup_type` | VARCHAR(50) | Setup type | |
| `termination_date` | INTEGER | Churn date | NULL = active |
| `termination_value` | DECIMAL(10,2) | Final value | |
| `transferred_contract` | BOOLEAN | Contract transfer | |
| `type_id` | INTEGER | Merchant type | FK to taxonomy |
| `cashier_ids` | TEXT | Cashier user IDs | Pipe-separated |
| `manager_ids` | TEXT | Manager user IDs | Pipe-separated |
| `driver_ids` | TEXT | Driver user IDs | Pipe-separated |
| `payment_terminal_ids` | TEXT | Terminal IDs | Pipe-separated |
| `kitchen_staff_ids` | TEXT | Kitchen staff IDs | Pipe-separated |
| `contact_name` | VARCHAR(255) | Contact person | |
| `description` | TEXT | Business description | Marketing copy |
| `cuisine_ids` | TEXT | Cuisine types | Comma-separated |
| `trainee_mode` | BOOLEAN | Training mode | 0 = production |
| `demo_mode` | BOOLEAN | Demo account | 0 = real |
| `default_order_type_cashier` | VARCHAR(50) | Default for cashier | |
| `default_order_type_customer` | VARCHAR(50) | Default for customer | |
| `show_bestsellers` | BOOLEAN | Show bestseller tags | |
| `use_quick_search` | BOOLEAN | Enable quick search | |
| `display_cashier_images` | BOOLEAN | Show cashier images | |
| `display_created_by` | BOOLEAN | Show creator info | |
| `use_customer_facing_display` | BOOLEAN | CFD enabled | |
| `timezone` | VARCHAR(50) | Timezone | Europe/Copenhagen |
| `contact_language` | VARCHAR(5) | Preferred language | da/en |
| `business_name` | VARCHAR(255) | Legal name | |
| `area` | VARCHAR(255) | City/postal area | |
| `street_address` | TEXT | Full address | |
| `suppress_receipt_prompt` | BOOLEAN | Auto-print receipts | |
| `print_on_acceptance` | BOOLEAN | Print on order accept | |
| `enable_receipt_download` | BOOLEAN | Download receipts | |
| `enable_email_receipts` | BOOLEAN | Email receipts | |
| `customer_receipt_cc` | VARCHAR(255) | Receipt CC email | |
| `customer_receipt_msg` | TEXT | Custom receipt message | |
| `daily_sales_reports` | BOOLEAN | Send daily reports | |
| `monthly_sales_reports` | BOOLEAN | Send monthly reports | |
| `sales_report_email` | VARCHAR(255) | Report destination | |
| `logo` | TEXT | Logo URL | Cloud storage |
| `image_1` to `image_5` | TEXT | Additional images | Cloud storage |
| `phone` | VARCHAR(20) | Public phone | |
| `email` | VARCHAR(255) | Public email | |
| `website` | TEXT | Website URL | |
| `facebook` | TEXT | Facebook URL | |
| `instagram` | TEXT | Instagram URL | |
| `takeaway_link` | TEXT | Takeaway deep link | |
| `delivery_link` | TEXT | Delivery deep link | |
| `table_booking_link` | TEXT | Booking deep link | |
| `opening_hours` | JSON | Opening hours | JSON format |
| `enable_cashback` | BOOLEAN | Cashback program | |
| `enable_voucher_payment` | BOOLEAN | Voucher payments | |
| `inventory_management` | BOOLEAN | Inventory module enabled | **CRITICAL FOR ML** |
| `seasonal` | BOOLEAN | Seasonal business | |
| `moved_to_competition` | BOOLEAN | Lost to competitor | Churn reason |
| `dormant` | BOOLEAN | Inactive account | |
| `dormant_partner` | BOOLEAN | Inactive partner | |
| `dead_lead` | BOOLEAN | Dead lead flag | |
| `closed` | BOOLEAN | Permanently closed | |
| Many operational flags... | | See full schema | 100+ columns total |

**Indexes:**
- PRIMARY: `id`
- INDEX: `active`, `termination_date`, `area_id`, `inventory_management`

**ML Usage**: Location features (area, cuisine type), business status for cohort analysis

---

##### `dim_users` - Users (Staff & Customers)
**Purpose**: Contains internal staff, merchant employees, AND end-customers

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Parent/creator user | Self-referential |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `account_closure_requested` | BOOLEAN | Closure request | |
| `age_group_id` | INTEGER | Age bracket | FK to taxonomy |
| `app_version` | VARCHAR(20) | App version | |
| `area_id` | INTEGER | Geographic area | FK to taxonomy |
| `cltv` | DECIMAL(10,2) | Customer lifetime value | Calculated metric |
| `country` | VARCHAR(2) | Country code | |
| `currency` | VARCHAR(3) | Preferred currency | |
| `date_of_birth` | DATE | Birth date | |
| `do_not_contact` | BOOLEAN | DNC flag | GDPR compliance |
| `first_name` | VARCHAR(100) | First name | |
| `gender_id` | INTEGER | Gender | FK to taxonomy |
| `last_name` | VARCHAR(100) | Last name | |
| `mobile_phone` | VARCHAR(20) | Phone number | |
| `picture` | TEXT | Profile image URL | |
| `orders` | INTEGER | Total order count | Aggregated |
| `redeemed_points` | INTEGER | Loyalty points used | |
| `referring_user_id` | INTEGER | Referrer user | FK to self |
| `referring_place_id` | INTEGER | Referrer location | FK to places |
| `savings` | DECIMAL(10,2) | Total savings | From discounts |
| `source` | VARCHAR(100) | Acquisition source | Marketing channel |
| `type` | VARCHAR(50) | User type | **admin/merchant_user/consumer** |
| `api_key` | VARCHAR(255) | API access key | For integrations |
| `roles` | TEXT | User roles | Comma-separated |
| `email` | VARCHAR(255) | Email address | |
| `password` | VARCHAR(255) | Hashed password | BCrypt/Argon2 |
| `referral_id` | VARCHAR(100) | Referral code | Unique code |
| `otp` | VARCHAR(10) | One-time password | 2FA |
| `language` | VARCHAR(5) | Preferred language | |
| `email_temp` | VARCHAR(255) | Temporary email | During verification |
| `mobile_phone_temp` | VARCHAR(20) | Temporary phone | During verification |
| `mobile_phone_valid` | BOOLEAN | Phone verified | |
| `email_valid` | BOOLEAN | Email verified | |
| `barcode_scanner_ids` | TEXT | Assigned scanners | |
| `receipt_printer_ids` | TEXT | Assigned printers | |
| `payment_terminal_ids` | TEXT | Assigned terminals | |
| `notifications` | BOOLEAN | Notifications enabled | |
| `favorite_place_ids` | TEXT | Favorite locations | |

**Indexes:**
- PRIMARY: `id`
- INDEX: `type`, `email`, `mobile_phone`
- UNIQUE: `email`, `mobile_phone`

**ML Usage**: Customer segmentation, purchase behavior analysis

---

##### `dim_taxonomy_terms` - Global Lookup/Tags
**Purpose**: Central reference table for all categories, tags, and classification lists

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | DATE | Creation date | YYYY-MM-DD |
| `updated` | DATE | Last update | YYYY-MM-DD |
| `vocabulary` | VARCHAR(100) | List type | area/cuisine/sales_outcome/age_group/gender |
| `name` | VARCHAR(255) | Term value | Human-readable label |

**Vocabularies:**
- `area`: Geographic regions
- `cuisine`: Cuisine types (Italian, Asian, etc.)
- `sales_outcome`: Sales pipeline outcomes
- `age_group`: Age brackets for demographics
- `gender`: Gender classifications

**Indexes:**
- PRIMARY: `id`
- INDEX: `vocabulary`, `name`
- COMPOSITE: `vocabulary` + `name`

---

#### **D. Campaigns & Marketing**

##### `dim_campaigns` - Campaign Definitions
**Purpose**: Marketing campaign master data

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | DATETIME | Creation date | Human-readable |
| `updated` | DATETIME | Last update | Human-readable |
| `place_id` | INTEGER | Target location | FK to dim_places |
| `status` | VARCHAR(20) | Campaign status | Active/Inactive |
| `type` | VARCHAR(100) | Campaign type | Discount/Promotion |
| `created` (duplicate) | INTEGER | UNIX timestamp | |
| `updated` (duplicate) | INTEGER | UNIX timestamp | |

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`, `status`

---

### 2. TRANSACTIONAL DATA (Fact Tables)

These tables store business events and transactions.

#### **A. Order & Sales**

##### `fct_orders` - Customer Orders
**Purpose**: Main order header records

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Customer user ID | FK to dim_users |
| `created` | INTEGER | Order timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `updated_by` | INTEGER | Last editor | FK to dim_users |
| `account_id` | INTEGER | Account reference | |
| `cash_amount` | DECIMAL(10,2) | Cash paid | DKK |
| `cashier_notified` | BOOLEAN | Cashier alerted | |
| `channel` | VARCHAR(50) | Order channel | App/Kiosk/Counter |
| `customer_mobile_phone` | VARCHAR(20) | Customer phone | |
| `customer_name` | VARCHAR(255) | Customer name | |
| `code` | VARCHAR(100) | Order code | |
| `delivery_charge` | DECIMAL(10,2) | Delivery fee | DKK |
| `delivery_location_id` | INTEGER | Delivery address | FK to locations |
| `demo_mode` | BOOLEAN | Demo flag | 0 = real |
| `discount_amount` | DECIMAL(10,2) | Total discount | DKK |
| `driver_id` | INTEGER | Assigned driver | FK to dim_users |
| `external_id` | VARCHAR(255) | External system ID | Integration |
| `instructions` | TEXT | Special instructions | |
| `items_amount` | DECIMAL(10,2) | Subtotal | Before fees |
| `payment_method` | VARCHAR(50) | Payment type | Cash/Card/MobilePay |
| `pickup_time` | INTEGER | Scheduled pickup | UNIX timestamp |
| `place_id` | INTEGER | Merchant location | FK to dim_places |
| `points_earned` | INTEGER | Loyalty points earned | |
| `points_redeemed` | INTEGER | Loyalty points used | |
| `promise_time` | INTEGER | Promised ready time | UNIX timestamp |
| `rejection_reason` | TEXT | Rejection reason | If cancelled |
| `referring_user_id` | INTEGER | Referrer | FK to dim_users |
| `service_charge` | DECIMAL(10,2) | Service fee | DKK |
| `source` | VARCHAR(100) | Order source | Customer/Integration |
| `split_bill` | BOOLEAN | Bill split enabled | |
| `split_bill_type` | VARCHAR(50) | Split method | |
| `status` | VARCHAR(50) | Order status | Pending/Closed/Cancelled |
| `synchronized_to_accounting` | BOOLEAN | Synced to accounting | |
| `table_id` | INTEGER | Table number | FK to dim_tables |
| `tier_id` | INTEGER | Customer tier | FK to tiers |
| `total_amount` | DECIMAL(10,2) | Grand total | DKK |
| `trainee_mode` | BOOLEAN | Training order | 0 = real |
| `type` | VARCHAR(50) | Order type | Eat-in/Takeaway/Delivery |
| `vat_amount` | DECIMAL(10,2) | VAT amount | DKK |

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`, `created`, `status`, `type`, `channel`
- COMPOSITE: `place_id` + `created`, `user_id` + `created`

**ML Usage**: PRIMARY DATA SOURCE for demand forecasting, seasonality patterns, channel preferences

---

##### `fct_order_items` - Order Line Items
**Purpose**: Individual items within each order

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Customer user ID | FK to dim_users |
| `created` | INTEGER | Item added time | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `title` | VARCHAR(255) | Item name | Display name |
| `campaign_id` | INTEGER | Applied campaign | FK to campaigns |
| `commission_amount` | DECIMAL(10,2) | Commission value | DKK |
| `cost` | DECIMAL(10,2) | Cost of goods sold | DKK |
| `discount_amount` | DECIMAL(10,2) | Item discount | DKK |
| `external_id` | VARCHAR(255) | External system ID | |
| `group` | VARCHAR(100) | Item grouping | |
| `instructions` | TEXT | Special requests | "No onions" |
| `item_id` | INTEGER | Menu item | FK to dim_menu_items |
| `order_id` | INTEGER | Parent order | FK to fct_orders |
| `points_earned` | INTEGER | Points earned | |
| `points_redeemed` | INTEGER | Points used | |
| `price` | DECIMAL(10,2) | Unit price | DKK |
| `quantity` | INTEGER | Quantity ordered | |
| `redemptions` | INTEGER | Promo redemptions | |
| `removed_ingredients` | TEXT | Removed items | "No pickles" |
| `add_on_ids` | TEXT | Selected add-ons | Comma-separated |
| `status` | VARCHAR(50) | Item status | Pending/Ready/Delivered |
| `vat_amount` | DECIMAL(10,2) | VAT on item | DKK |

**Indexes:**
- PRIMARY: `id`
- INDEX: `order_id`, `item_id`, `created`
- COMPOSITE: `item_id` + `created`

**ML Usage**: Item-level sales for popularity analysis, combo recommendations

---

#### **B. Inventory & Financial**

##### `fct_inventory_reports` - Inventory Snapshots
**Purpose**: Periodic stock level reports and variance tracking

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | INTEGER | Report timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `end_time` | INTEGER | Report end time | UNIX timestamp |
| `excel` | TEXT | Excel file URL | Cloud storage |
| `data` | JSON | Report data | JSON format |
| `pdf` | TEXT | PDF file URL | Cloud storage |
| `place_id` | INTEGER | Merchant location | FK to dim_places |
| `start_time` | INTEGER | Report start time | UNIX timestamp |

**Note**: This table structure suggests reports are stored as files. Detailed inventory data may be in JSON `data` field.

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`, `start_time`, `end_time`

**ML Usage**: Historical stock levels for trend analysis, waste prediction

---

##### `fct_cash_balances` - Cash Register Balancing
**Purpose**: Daily cash drawer reconciliation

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Responsible user | FK to dim_users |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `closing_coins_and_notes` | DECIMAL(10,2) | Physical cash count | DKK |
| `closing_balance` | DECIMAL(10,2) | Calculated close | DKK |
| `end_time` | INTEGER | Close timestamp | UNIX timestamp |
| `place_id` | INTEGER | Merchant location | FK to dim_places |
| `opening_balance` | DECIMAL(10,2) | Starting cash | DKK |
| `opening_coins_and_notes` | DECIMAL(10,2) | Physical open count | DKK |
| `status` | VARCHAR(50) | Balance status | Open/Closed |
| `transactions` | JSON | Transaction log | JSON array |

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`, `end_time`, `status`

**ML Usage**: Cash flow patterns, discrepancy detection

---

##### `fct_invoice_items` - Invoice Line Items
**Purpose**: Platform invoice items to merchants (B2B billing)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `amount` | DECIMAL(10,2) | Line item total | DKK |
| `product_id` | INTEGER | Product/service | FK to products |
| `description` | TEXT | Item description | "POS Light (76 days)" |
| `invoice_id` | INTEGER | Parent invoice | FK to invoices |

**Indexes:**
- PRIMARY: `id`
- INDEX: `invoice_id`, `product_id`

**ML Usage**: Revenue analysis, customer value

---

#### **C. Marketing & Promotions**

##### `fct_campaigns` - Campaign Execution
**Purpose**: Active campaign performance tracking

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | DATETIME | Creation date | Human-readable |
| `updated` | DATETIME | Last update | Human-readable |
| `title` | VARCHAR(255) | Campaign name | Display name |
| `auto_created` | BOOLEAN | Auto-generated | System flag |
| `item_ids` | TEXT | Target items | Comma-separated |
| `account_ids` | TEXT | Target accounts | Comma-separated |
| `delivery` | BOOLEAN | Applies to delivery | |
| `eat_in` | BOOLEAN | Applies to eat-in | |
| `takeaway` | BOOLEAN | Applies to takeaway | |
| `discount` | DECIMAL(10,2) | Discount value | % or fixed |
| `discount_type` | INTEGER | Discount type | 0=%, 1=fixed |
| `start_date_time` | DATETIME | Campaign start | |
| `end_date_time` | DATETIME | Campaign end | |
| `minimum_spend` | DECIMAL(10,2) | Min order value | DKK |
| `parent_id` | INTEGER | Parent campaign | For variants |
| `place_id` | INTEGER | Merchant location | FK to dim_places |
| `provider` | INTEGER | Campaign provider | |
| `redemptions` | INTEGER | Max redemptions | Per campaign |
| `redemptions_per_customer` | INTEGER | Max per customer | |
| `status` | VARCHAR(50) | Campaign status | Active/Inactive |
| `table_id` | INTEGER | Specific table | FK to dim_tables |
| `type` | VARCHAR(100) | Campaign type | Discount type |
| `used_redemptions` | INTEGER | Redemptions used | Counter |
| `variation` | INTEGER | Campaign variation | A/B testing |

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`, `status`, `start_date_time`, `end_date_time`

**ML Usage**: Campaign effectiveness, optimal discount levels

---

##### `fct_bonus_codes` - Promotional Codes
**Purpose**: Coupon/bonus code management

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `id` | INTEGER | Primary key | Auto-increment |
| `user_id` | INTEGER | Creator user ID | FK to dim_users |
| `created` | INTEGER | Creation timestamp | UNIX timestamp |
| `updated` | INTEGER | Last update | UNIX timestamp |
| `end_date_time` | INTEGER | Expiration time | UNIX timestamp |
| `start_date_time` | INTEGER | Activation time | UNIX timestamp |
| `place_id` | INTEGER | Applicable location | FK to dim_places |
| `points` | INTEGER | Loyalty points value | |
| `redemptions` | INTEGER | Times used | Counter |

**Indexes:**
- PRIMARY: `id`
- INDEX: `place_id`, `start_date_time`, `end_date_time`

---

### 3. AGGREGATED VIEWS

##### `most_ordered` - Top Selling Items
**Purpose**: Pre-computed bestseller list by location

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `place_id` | INTEGER | Merchant location | FK to dim_places |
| `device_product` | DECIMAL | Device product flag | |
| `item_id` | INTEGER | Menu item | FK to dim_menu_items |
| `item_name` | VARCHAR(255) | Item name | Display name |
| `order_count` | INTEGER | Total orders | Aggregated count |

**Indexes:**
- COMPOSITE: `place_id` + `order_count` DESC

**ML Usage**: Popularity features, recommendation baseline

---

## Relationships & Foreign Keys

### Star Schema Design

```
             ┌──────────────────┐
             │  dim_places      │
             │  (Merchants)     │
             └────────┬─────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
  ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
  │fct_orders│   │fct_camp-│   │fct_inven│
  │         │   │aigns    │   │tory     │
  └─────┬───┘   └─────────┘   └─────────┘
        │
   ┌────▼──────────┐
   │fct_order_items│
   └────┬──────────┘
        │
   ┌────▼────────┐
   │dim_menu_    │
   │items        │
   └────┬────────┘
        │
   ┌────▼────────┐
   │dim_bill_of_ │
   │materials    │
   └────┬────────┘
        │
   ┌────▼────────┐
   │dim_skus     │
   └─────────────┘
```

### Key Relationships

1. **Orders to Items**: `fct_orders.id` ← `fct_order_items.order_id` (1:N)
2. **Menu to BOM**: `dim_menu_items.id` ← `dim_bill_of_materials.parent_sku_id` (1:N)
3. **BOM to Raw**: `dim_skus.id` ← `dim_bill_of_materials.sku_id` (1:N)
4. **Location Hub**: `dim_places.id` ← ALL fact tables via `place_id` (1:N)
5. **User Links**: `dim_users.id` ← Multiple tables via `user_id` (1:N)
6. **Categories**: `dim_stock_categories.id` ← `dim_skus.stock_category_id` (1:N)

---

## Machine Learning Integration

### Primary Use Cases

#### 1. **Demand Forecasting**
**Training Data Sources:**
- `fct_orders` + `fct_order_items`: Historical sales by item, time, location
- `dim_menu_items`: Item attributes (price, category)
- `dim_places`: Location features (area, cuisine type)
- `fct_campaigns`: Promotional impact
- **External**: Weather, holidays, events

**Features to Engineer:**
- Rolling averages (7-day, 30-day sales)
- Day of week, hour of day
- Seasonality indicators
- Price elasticity
- Campaign binary flags

**Target Variables:**
- Daily demand per item
- Weekly demand per category
- Prep quantities needed

---

#### 2. **Inventory Optimization**
**Training Data Sources:**
- `dim_skus`: Current stock levels, reorder points
- `dim_bill_of_materials`: Recipe ingredient requirements
- `fct_order_items`: Actual consumption rates
- `fct_inventory_reports`: Historical stock variances

**Features:**
- Lead time for reordering
- Shelf life/expiration dates
- Historical stockout frequency
- Demand volatility (std dev)

**Target Variables:**
- Optimal reorder point
- Economic order quantity (EOQ)
- Safety stock levels
- Waste prediction

---

#### 3. **Price Optimization**
**Training Data Sources:**
- `dim_menu_items`: Current pricing, sales history
- `fct_order_items`: Sales volume by price point
- `fct_campaigns`: Discount effectiveness

**Features:**
- Price elasticity of demand
- Competitor pricing (external)
- Cost of goods sold
- Cross-item effects

**Target Variables:**
- Optimal price point
- Revenue maximization
- Margin optimization

---

### Real-Time Update Flows

```
┌─────────────────────┐
│   Website/API       │
│   (Order Placed)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   fct_orders        │◄── INSERT new order
│   fct_order_items   │◄── INSERT line items
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   dim_skus          │◄── UPDATE quantity (decrement)
│   (Inventory)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ML Model          │◄── Trigger retraining if threshold
│   (Async Queue)     │    (e.g., daily batch)
└─────────────────────┘
```

---

## API Endpoints Schema

### Suggested REST API Structure

#### **Inventory Management**

```
GET    /api/inventory/items                 - List all inventory items
GET    /api/inventory/items/:id             - Get item details
POST   /api/inventory/items                 - Create new item
PUT    /api/inventory/items/:id             - Update item
DELETE /api/inventory/items/:id             - Delete item (soft delete)

GET    /api/inventory/skus                  - List SKUs with stock levels
GET    /api/inventory/skus/low-stock        - Get items below threshold
PUT    /api/inventory/skus/:id/quantity     - Update stock quantity

GET    /api/inventory/categories            - List stock categories
POST   /api/inventory/categories            - Create category

GET    /api/inventory/reports               - List inventory reports
POST   /api/inventory/reports               - Generate new report
GET    /api/inventory/reports/:id           - Download report (PDF/Excel)
```

#### **Menu Management**

```
GET    /api/menu/items                      - List menu items
GET    /api/menu/items/:id                  - Get menu item details
POST   /api/menu/items                      - Create menu item
PUT    /api/menu/items/:id                  - Update menu item
DELETE /api/menu/items/:id                  - Remove from menu

GET    /api/menu/items/:id/bom              - Get recipe/BOM
PUT    /api/menu/items/:id/bom              - Update recipe

GET    /api/menu/add-ons                    - List add-ons
POST   /api/menu/add-ons                    - Create add-on
```

#### **Orders**

```
GET    /api/orders                          - List orders (with filters)
GET    /api/orders/:id                      - Get order details
POST   /api/orders                          - Create new order
PUT    /api/orders/:id/status               - Update order status

GET    /api/orders/stats/daily              - Daily sales stats
GET    /api/orders/stats/popular            - Most ordered items
```

#### **Analytics & ML**

```
GET    /api/analytics/demand-forecast       - Get demand predictions
POST   /api/analytics/demand-forecast       - Trigger forecast refresh

GET    /api/analytics/inventory-optimization - Get reorder suggestions
GET    /api/analytics/waste-prediction      - Predicted waste by item

GET    /api/analytics/price-recommendations - Price optimization suggestions
```

#### **Campaigns**

```
GET    /api/campaigns                       - List campaigns
POST   /api/campaigns                       - Create campaign
PUT    /api/campaigns/:id                   - Update campaign
GET    /api/campaigns/:id/performance       - Campaign metrics
```

---

## Database Setup Instructions

### 1. **Choose Database System**

For this project, recommended options:

- **PostgreSQL** (Recommended): Best for complex queries, JSON support, advanced indexing
- **MySQL/MariaDB**: Wide support, good performance
- **SQLite**: For development/testing only

### 2. **Create Database**

```sql
CREATE DATABASE fresh_flow_inventory
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### 3. **Import CSV Data**

**Option A: Using Python (Recommended)**

```python
import pandas as pd
from sqlalchemy import create_engine

# Create database connection
engine = create_engine('postgresql://user:password@localhost/fresh_flow_inventory')

# Load CSV files
tables = {
    'dim_items': 'data/Inventory Management/dim_items.csv',
    'dim_skus': 'data/Inventory Management/dim_skus.csv',
    'fct_orders': 'data/Inventory Management/fct_orders.csv',
    # ... add all tables
}

for table_name, csv_path in tables.items():
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Loaded {table_name}: {len(df)} rows")
```

**Option B: Direct SQL Import (PostgreSQL)**

```bash
psql -U username -d fresh_flow_inventory << EOF
\COPY dim_items FROM 'data/Inventory Management/dim_items.csv' CSV HEADER;
\COPY dim_skus FROM 'data/Inventory Management/dim_skus.csv' CSV HEADER;
-- ... repeat for all tables
EOF
```

### 4. **Create Indexes**

```sql
-- Inventory indexes
CREATE INDEX idx_skus_stock_category ON dim_skus(stock_category_id);
CREATE INDEX idx_skus_quantity ON dim_skus(quantity);
CREATE INDEX idx_bom_parent ON dim_bill_of_materials(parent_sku_id);

-- Order indexes
CREATE INDEX idx_orders_place_created ON fct_orders(place_id, created);
CREATE INDEX idx_orders_status ON fct_orders(status);
CREATE INDEX idx_order_items_item ON fct_order_items(item_id);

-- Full-text search
CREATE INDEX idx_items_fulltext ON dim_items USING gin(to_tsvector('english', title || ' ' || description));
```

### 5. **Set Up Foreign Keys (Optional but Recommended)**

```sql
ALTER TABLE fct_orders 
    ADD CONSTRAINT fk_orders_place 
    FOREIGN KEY (place_id) REFERENCES dim_places(id);

ALTER TABLE fct_order_items 
    ADD CONSTRAINT fk_order_items_order 
    FOREIGN KEY (order_id) REFERENCES fct_orders(id);

ALTER TABLE dim_skus 
    ADD CONSTRAINT fk_skus_category 
    FOREIGN KEY (stock_category_id) REFERENCES dim_stock_categories(id);

-- Add more as needed
```

---

## Data Cleaning & Preprocessing

### Issues to Address

Based on the README, the following cleaning has been done:

1. ✅ **Missing Values**: Filled with defaults (0 for IDs, 'none' for text, 'unknown' for categorical)
2. ✅ **Duplicates**: Removed based on unique ID fields
3. ✅ **Outliers**: Z-score method (threshold 2-3) applied to numeric columns
4. ✅ **Type Conversion**: Unix timestamps converted to readable dates
5. ✅ **Data Validation**: Records with missing critical fields (price, status) dropped

### Additional Preprocessing for ML

```python
import pandas as pd
from datetime import datetime

# Convert Unix timestamps
df['created_dt'] = pd.to_datetime(df['created'], unit='s')
df['day_of_week'] = df['created_dt'].dt.dayofweek
df['hour'] = df['created_dt'].dt.hour
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

# Handle JSON fields
df['opening_hours'] = df['opening_hours'].apply(json.loads)

# Parse pipe-separated IDs
df['cuisine_list'] = df['cuisine_ids'].str.split('|')

# Encode categorical variables
df = pd.get_dummies(df, columns=['type', 'status', 'channel'])

# Create lag features for time series
df['sales_7d_avg'] = df.groupby('item_id')['quantity'].transform(
    lambda x: x.rolling(7, min_periods=1).mean()
)
```

---

## Backup & Maintenance

### Daily Tasks

```bash
# Automated backup script
pg_dump fresh_flow_inventory | gzip > backups/fresh_flow_$(date +%Y%m%d).sql.gz

# Vacuum analyze (PostgreSQL)
psql -d fresh_flow_inventory -c "VACUUM ANALYZE;"
```

### Weekly Tasks

```sql
-- Update aggregated views
REFRESH MATERIALIZED VIEW most_ordered;

-- Check for data quality issues
SELECT place_id, COUNT(*) as orphan_orders
FROM fct_orders
WHERE place_id NOT IN (SELECT id FROM dim_places)
GROUP BY place_id;
```

---

## Security Considerations

### API Layer

- **Authentication**: JWT tokens for API access
- **Authorization**: Role-based access control (RBAC)
  - `admin`: Full access
  - `merchant_user`: Access to own place_id only
  - `consumer`: Read-only, own data only

### Database

```sql
-- Create read-only user for ML models
CREATE USER ml_readonly WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE fresh_flow_inventory TO ml_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ml_readonly;

-- Create API user with limited write access
CREATE USER api_user WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE ON fct_orders, fct_order_items TO api_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO api_user;
```

### Data Privacy

- **PII Protection**: Encrypt `dim_users` sensitive fields (email, phone, password)
- **GDPR Compliance**: Implement soft deletes, data export APIs
- **Anonymization**: For ML training, hash user IDs

---

## Performance Optimization

### Query Optimization

```sql
-- Use materialized views for heavy aggregations
CREATE MATERIALIZED VIEW daily_sales_summary AS
SELECT 
    DATE(FROM_UNIXTIME(created)) as sale_date,
    place_id,
    type as order_type,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue
FROM fct_orders
WHERE status = 'Closed'
GROUP BY 1, 2, 3;

-- Partition large tables by date
CREATE TABLE fct_orders_partitioned (
    -- columns
) PARTITION BY RANGE (created);

CREATE TABLE fct_orders_2025_01 PARTITION OF fct_orders_partitioned
    FOR VALUES FROM (1704067200) TO (1706745600);
```

### Caching Strategy

- **Application Layer**: Redis for frequently accessed data (menu items, popular products)
- **Database**: Query result caching for analytics endpoints
- **CDN**: Static assets (images, PDFs)

---

## Monitoring & Alerts

### Key Metrics to Track

1. **Inventory Alerts**
   - Items below `low_stock_threshold`
   - High variance in `fct_inventory_reports`

2. **Sales Anomalies**
   - Sudden drop/spike in order volume
   - Unusually high discount redemptions

3. **System Health**
   - Database connection pool utilization
   - Query response times > 1s
   - Failed API requests

### Alert Configuration

```sql
-- Low stock alert query
SELECT s.id, s.title, s.quantity, s.low_stock_threshold
FROM dim_skus s
WHERE s.quantity <= s.low_stock_threshold
    AND s.quantity > 0;

-- Daily sales comparison (detect anomalies)
SELECT 
    place_id,
    COUNT(*) as today_orders,
    AVG(COUNT(*)) OVER (
        PARTITION BY place_id 
        ORDER BY DATE(FROM_UNIXTIME(created))
        ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    ) as avg_last_7_days
FROM fct_orders
WHERE DATE(FROM_UNIXTIME(created)) = CURDATE()
GROUP BY place_id
HAVING today_orders < avg_last_7_days * 0.5;  -- 50% drop
```

---

## Next Steps

### For Backend Development

1. **Set up database** using PostgreSQL/MySQL
2. **Create ORM models** (SQLAlchemy/Django ORM)
3. **Build REST API** using Flask/FastAPI/Django
4. **Implement authentication** (JWT tokens)
5. **Create data validation** schemas (Pydantic)

### For ML Integration

1. **Extract training data** from fact tables
2. **Feature engineering** pipeline
3. **Train baseline models** (ARIMA, Prophet, XGBoost)
4. **Build prediction API** endpoints
5. **Set up retraining** automation (daily/weekly)

### For Frontend

1. **Design dashboard** layouts
2. **Connect to API** endpoints
3. **Build visualization** components (charts, tables)
4. **Implement real-time** updates (WebSockets/polling)

---

## Sample Queries

### Business Intelligence Queries

```sql
-- Top 10 bestselling items this month
SELECT 
    mi.title,
    COUNT(oi.id) as order_count,
    SUM(oi.quantity) as total_sold,
    SUM(oi.price * oi.quantity) as revenue
FROM fct_order_items oi
JOIN dim_menu_items mi ON oi.item_id = mi.id
JOIN fct_orders o ON oi.order_id = o.id
WHERE o.created >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 1 MONTH))
    AND o.status = 'Closed'
GROUP BY mi.id, mi.title
ORDER BY total_sold DESC
LIMIT 10;

-- Calculate required raw materials for tomorrow's forecast
SELECT 
    i.title as ingredient,
    SUM(bom.quantity * forecast.predicted_qty) as required_qty,
    s.quantity as current_stock,
    s.unit,
    CASE 
        WHEN s.quantity < SUM(bom.quantity * forecast.predicted_qty) 
        THEN SUM(bom.quantity * forecast.predicted_qty) - s.quantity
        ELSE 0
    END as shortage
FROM ml_demand_forecast forecast
JOIN dim_menu_items mi ON forecast.item_id = mi.id
JOIN dim_bill_of_materials bom ON mi.id = bom.parent_sku_id
JOIN dim_skus s ON bom.sku_id = s.id
JOIN dim_items i ON s.item_id = i.id
WHERE forecast.forecast_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
GROUP BY i.id, i.title, s.quantity, s.unit;

-- Customer lifetime value
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as lifetime_value,
    AVG(o.total_amount) as avg_order_value,
    MAX(FROM_UNIXTIME(o.created)) as last_order_date
FROM dim_users u
JOIN fct_orders o ON u.id = o.user_id
WHERE u.type = 'consumer'
    AND o.status = 'Closed'
GROUP BY u.id
ORDER BY lifetime_value DESC
LIMIT 100;
```

---

## Glossary

- **BOM**: Bill of Materials - recipe breakdown of ingredients
- **CLTV**: Customer Lifetime Value
- **DKK**: Danish Krone (currency)
- **FK**: Foreign Key
- **GDPR**: General Data Protection Regulation
- **ISV**: Independent Software Vendor
- **PII**: Personally Identifiable Information
- **SKU**: Stock Keeping Unit
- **UNIX Timestamp**: Seconds since January 1, 1970 00:00:00 UTC
- **VAT**: Value Added Tax

---

## Support & Contribution

For questions or improvements to this schema:

1. Check existing database patterns
2. Validate changes don't break ML pipelines
3. Update this documentation with any schema changes
4. Run migration scripts for production changes

---

**Last Updated**: February 3, 2026
**Version**: 1.0
**Maintained By**: Cloud/Backend Team
