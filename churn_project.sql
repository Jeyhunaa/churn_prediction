-- Create the Table Schema
CREATE TABLE ecommerce_churn (
    CustomerID INT PRIMARY KEY,
    Churn INT,
    Tenure FLOAT,
    PreferredLoginDevice VARCHAR(50),
    CityTier INT,
    WarehouseToHome FLOAT,
    PreferredPaymentMode VARCHAR(50),
    Gender VARCHAR(20),
    HourSpendOnApp FLOAT,
    NumberOfDeviceRegistered INT,
    PreferedOrderCat VARCHAR(50),
    SatisfactionScore INT,
    MaritalStatus VARCHAR(20),
    NumberOfAddress INT,
    Complain INT,
    OrderAmountHikeFromlastYear FLOAT,
    CouponUsed FLOAT,
    OrderCount FLOAT,
    DaySinceLastOrder FLOAT,
    CashbackAmount FLOAT
);

-- Check total row count
SELECT COUNT(*) FROM ecommerce_churn;

-- View the first 10 rows to ensure columns align
SELECT * FROM ecommerce_churn LIMIT 10;

CREATE OR REPLACE VIEW v_ecommerce_cleaned AS
SELECT
    CustomerID AS customerid,
    CAST(Churn AS INT) AS churn,
    Tenure AS tenure,

    -- 1. Standardizing Device Names
    CASE
        WHEN PreferredLoginDevice IN ('Phone', 'Mobile Phone') THEN 'Mobile Phone'
        WHEN PreferredLoginDevice = 'Computer' THEN 'Computer'
        ELSE 'Other'
    END AS preferredlogindevice,

    CityTier AS citytier,
    WarehouseToHome AS warehousetohome,

    -- 2. Standardizing Payment Modes (Dataset has CC, COD, and various card types)
    CASE
        WHEN PreferredPaymentMode = 'CC' THEN 'Credit Card'
        WHEN PreferredPaymentMode = 'COD' THEN 'Cash on Delivery'
        WHEN PreferredPaymentMode = 'Debit Card' THEN 'Debit Card'
        WHEN PreferredPaymentMode = 'Credit Card' THEN 'Credit Card'
        WHEN PreferredPaymentMode = 'UPI' THEN 'UPI'
        ELSE 'E-Wallet'
    END AS preferredpaymentmode,

    Gender AS gender,
    HourSpendOnApp AS hourspendonapp,
    NumberOfDeviceRegistered AS numberofdeviceregistered,

    -- 3. Standardizing Order Categories
    CASE
        WHEN PreferedOrderCat = 'Mobile' THEN 'Mobile Phone'
        WHEN PreferedOrderCat = 'Mobile Phone' THEN 'Mobile Phone'
        ELSE PreferedOrderCat
    END AS preferedordercat,

    SatisfactionScore AS satisfactionscore,
    MaritalStatus AS maritalstatus,
    NumberOfAddress AS numberofaddress,
    CAST(Complain AS INT) AS complain,
    OrderAmountHikeFromlastYear AS orderamounthikefromlastyear,
    CouponUsed AS couponused,
    OrderCount AS ordercount,
    DaySinceLastOrder AS daysincelastorder,
    CashbackAmount AS cashbackamount

FROM ecommerce_churn;


SELECT cashbackamount, complain, churn
from ecommerce_churn
where Complain = 1 and CashbackAmount >= 150;

SELECT churn, COUNT(*) AS count
FROM ecommerce_churn
WHERE Complain = 1 AND CashbackAmount >= 150
GROUP BY churn;



SELECT *FROM v_ecommerce_cleaned