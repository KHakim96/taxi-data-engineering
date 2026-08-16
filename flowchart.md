flowchart LR
    %% ================= EXTERNAL SOURCES =================
    subgraph SRC["EXTERNAL SOURCES"]
        SRC_TAXI["BigQuery public data<br/>chicago_taxi_trips 2013-2023"]
        SRC_WX["Open-Meteo Archive API<br/>Chicago daily weather"]
        SRC_HOL["Nager.Date API<br/>US public holidays"]
    end

    %% ================= INGESTION =================
    subgraph ING["PYTHON INGESTION"]
        ING_WX["fetch_weather.py<br/>WRITE_TRUNCATE load"]
        ING_HOL["fetch_holidays.py<br/>WRITE_TRUNCATE load"]
    end

    %% ================= BRONZE =================
    subgraph BRZ["BRONZE - RAW / INGESTED"]
        RAW_TAXI["raw_taxi_trips<br/>raw trip landing"]
        RAW_WX["raw_weather<br/>raw daily weather"]
        RAW_HOL["raw_holidays<br/>raw holiday rows"]
    end

    %% ================= SILVER =================
    subgraph SIL["SILVER - CLEANED / STANDARDIZED"]
        STG_TAXI["stg_taxi_trips<br/>dedup - Chicago TZ - plausibility flags"]
        STG_WX["stg_weather<br/>typed - 1 row per date"]
        STG_HOL["stg_holidays<br/>distinct - is_holiday flag"]
    end

    %% ================= DATA QUALITY GATE =================
    subgraph DQ["DATA QUALITY GATE - 14 DATAFORM ASSERTIONS"]
        DQ_TAXI["taxi x6 on stg_taxi_trips<br/>unique key - positives - valid timestamps"]
        DQ_VEH["vehicle x1 on vehicle_activity_day<br/>active-minutes bounded"]
        DQ_WX["weather x5 on stg_weather<br/>1 row/date - temps - precip >= 0"]
        DQ_HOL["holidays x2 on stg_holidays<br/>1 row/date - date not null"]
    end

    %% ================= GOLD (ONE CONTAINER) =================
    subgraph GOLD["GOLD - BUSINESS-READY / ANALYTICS"]
        subgraph GDIM["DIMENSIONS"]
            DW["dim_weather<br/>conformed daily weather"]
            DH["dim_holiday<br/>conformed holidays"]
            DCA["dim_chicago_community_area<br/>77 areas - hardcoded"]
        end
        subgraph GFCT["FACTS"]
            FTT["fact_taxi_trip<br/>trip-grain trusted fact"]
            FDM["fact_daily_demand<br/>1 row/day - trips x wx x holiday"]
        end
        subgraph GANA["ANALYTICAL MODELS"]
            VAD["vehicle_activity_day<br/>taxi x day active-time model"]
            PG["pickup_geospatial<br/>pickup metrics per area x day"]
        end
        subgraph GREP["REPORT MARTS"]
            EXEC["executive_dashboard<br/>executive OBT for Looker"]
            BI2["business_insight_2<br/>taxi company performance"]
            TE["tip_earners<br/>daily tips per taxi"]
            HWI["holiday_weather_impact<br/>holiday vs weekday vs weekend"]
            OVW["overworkers<br/>vehicle-day utilization"]
            FCD["forecast_dashboard<br/>actuals + ML predictions"]
            BI1["business_insight_1<br/>daily ops KPIs - no consumer yet"]
            FE["forecast_features<br/>daily ML features - no consumer yet"]
        end
    end

    %% ================= ML =================
    subgraph ML["ML - XGBOOST FORECASTING (PYTHON)"]
        MLP["train.py / predict.py / evaluate.py<br/>lag_1 - lag_7 - rolling_7d features<br/>train < 2023 - predict 2023"]
        MPU["upload_predictions.py"]
        MP["ml.model_predictions<br/>declared in Dataform"]
    end

    %% ================= LOOKER =================
    subgraph LKR["LOOKER STUDIO - BI"]
        LK["Looker Studio dashboards<br/>Executive - Taxi Performance<br/>Demand Factors - Overworkers<br/>Forecast"]
    end

    %% ---- sources -> ingestion -> bronze ----
    SRC_TAXI -->|"dataform query - no script"| RAW_TAXI
    SRC_WX --> ING_WX --> RAW_WX
    SRC_HOL --> ING_HOL --> RAW_HOL

    %% ---- bronze -> silver ----
    RAW_TAXI --> STG_TAXI
    RAW_WX --> STG_WX
    RAW_HOL --> STG_HOL

    %% ---- quality gate (control, not data) ----
    SIL -.->|"validated by"| DQ
    DQ -.->|"fail blocks build"| GOLD

    %% ---- silver -> gold (data lineage) ----
    STG_TAXI --> FTT
    STG_TAXI --> VAD
    STG_WX --> DW
    STG_HOL --> DH
    STG_TAXI --> PG
    STG_WX --> PG
    STG_HOL --> PG
    DCA --> PG

    %% ---- gold internal ----
    FTT --> FDM
    DW --> FDM
    DH --> FDM
    FTT --> EXEC
    DW --> EXEC
    DH --> EXEC
    DCA --> EXEC
    FTT --> BI1
    FTT --> BI2
    FTT --> TE
    FTT --> FE
    VAD --> OVW
    FDM --> HWI
    FDM --> FCD

    %% ---- ML loop ----
    FDM -->|"direct BQ read"| MLP
    MLP --> MPU --> MP
    MP -->|"ref() declaration"| FCD

    %% ---- gold reports -> looker ----
    EXEC --> LK
    BI2 --> LK
    TE --> LK
    HWI --> LK
    OVW --> LK
    FCD --> LK
    PG --> LK

    %% ================= STYLING =================
    classDef src fill:#e8eaed,stroke:#5f6368,color:#202124
    classDef bronze fill:#fce8e6,stroke:#c5221f,color:#202124
    classDef silver fill:#e8f0fe,stroke:#1a73e8,color:#202124
    classDef gold fill:#fef7e0,stroke:#f9ab00,color:#202124
    classDef report fill:#e6f4ea,stroke:#137333,color:#202124
    classDef ml fill:#f3e8fd,stroke:#8430ce,color:#202124
    classDef bi fill:#0047ab,stroke:#0047ab,color:#ffffff
    classDef gate fill:#ffffff,stroke:#d93025,color:#d93025,stroke-dasharray:3 3

    class SRC_TAXI,SRC_WX,SRC_HOL,ING_WX,ING_HOL src
    class RAW_TAXI,RAW_WX,RAW_HOL bronze
    class STG_TAXI,STG_WX,STG_HOL silver
    class DW,DH,DCA,FTT,FDM,VAD,PG gold
    class EXEC,BI1,BI2,TE,HWI,OVW,FCD,FE report
    class MLP,MPU,MP ml
    class LK bi
    class DQ_TAXI,DQ_VEH,DQ_WX,DQ_HOL gate