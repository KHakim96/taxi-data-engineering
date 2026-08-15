graph LR
    subgraph SRC["🌐 EXTERNAL SOURCES"]
        pub[" bigquery-public-data\nchicago_taxi_trips\n~200M rows "]
        weather_api[" Open-Meteo API\nhistorical weather "]
        holiday_api[" Nager.Date API\nUS holidays "]
    end

    subgraph ING["🐍 INGESTION - Python"]
        fetch_w[" fetch_weather.py\nrequests + load_to_bq "]
        fetch_h[" fetch_holidays.py\nrequests + load_to_bq "]
    end

    subgraph B["🥉 BRONZE\nBigQuery + Dataform"]
        raw_taxi[" raw_taxi_trips\nDataform: SELECT * "]
        raw_weather[" raw_weather\nPython: load_table "]
        raw_holidays[" raw_holidays\nPython: load_table "]
    end

    subgraph S["🥈 SILVER\nBigQuery + Dataform"]
        stg_taxi[" stg_taxi_trips\ndedup + timezone + label "]
        stg_weather[" stg_weather\ntyped + rain/snow flags "]
        stg_holidays[" stg_holidays\ndistinct + is_holiday "]
    end

    subgraph DQ["✅ DATA QUALITY CHECKPOINT\nDataform assertions"]
        asrt_taxi[" 7 taxi assertions\ndup/null unique_key\npositive miles, seconds, total\nvalid timestamps\nbounded vehicle-day activity "]
        asrt_weather[" 5 weather assertions\ndup/null weather_date\nnon-negative precip, snow\nvalid temperature "]
        asrt_holiday[" 2 holiday assertions\ndup/null holiday_date "]
    end

    subgraph G["🥇 GOLD\nBigQuery + Dataform"]
        subgraph GD["Dimensions"]
            dim_date["dim_date\n(orphan - unused)"]
            dim_weather["dim_weather"]
            dim_holiday["dim_holiday"]
            dim_area["dim_chicago\n_community_area"]
        end
        subgraph GF["Core Facts"]
            fact_trip[" fact_taxi_trip\nper trip "]
            fact_daily[" fact_daily_demand\nper day "]
        end
        subgraph GV["Vehicle Utilization Chain"]
            vad[" vehicle_activity_day\nper taxi × day\nsweep-line union "]
            over[" overworkers\nper taxi/day\n(Looker compat name) "]
        end
        subgraph GR["Reports"]
            exec["executive_dashboard"]
            hw["holiday_weather_impact"]
            bi1["business_insight_1"]
            bi2["business_insight_2"]
            geo["pickup_geospatial"]
            fc_feat["forecast_features"]
            fc_dash["forecast_dashboard"]
            tips["tip_earners"]
        end
    end

    subgraph M["🐍 ML PIPELINE\nPython + XGBoost"]
        train[" train.py\nXGBRegressor.fit\nyear < 2023 "]
        predict[" predict.py\nmodel.predict\nyear = 2023 "]
        upload[" upload_predictions.py\nload_table_from_dataframe "]
        preds[" ml.model_predictions\nBigQuery table\nDECLARED in Dataform "]
    end

    subgraph BI["📊 BI LAYER\nLooker Studio"]
        looker[" Looker Studio\ndata source: BigQuery "]
    end

    weather_api -->|HTTP GET| fetch_w
    holiday_api -->|HTTP GET| fetch_h
    fetch_w -->|load_table| raw_weather
    fetch_h -->|load_table| raw_holidays

    pub -->|Dataform: SELECT *| raw_taxi

    raw_taxi -->|Dataform SQL| stg_taxi
    raw_weather -->|Dataform SQL| stg_weather
    raw_holidays -->|Dataform SQL| stg_holidays

    stg_taxi -.->|validated by| asrt_taxi
    stg_weather -.->|validated by| asrt_weather
    stg_holidays -.->|validated by| asrt_holiday

    stg_taxi -->|Dataform SQL| dim_date
    stg_weather -->|Dataform SQL| dim_weather
    stg_holidays -->|Dataform SQL| dim_holiday
    stg_taxi -->|Dataform SQL| fact_trip
    fact_trip -->|Dataform SQL| fact_daily
    dim_weather -->|JOIN| fact_daily
    dim_holiday -->|JOIN| fact_daily
    stg_taxi -->|Dataform SQL\ninterval union per taxi-day| vad
    vad -->|Dataform SQL| over
    stg_taxi -->|Dataform SQL| geo
    stg_holidays -->|JOIN| geo
    stg_weather -->|JOIN| geo
    dim_area -->|JOIN| geo

    fact_trip -->|Dataform SQL| exec
    dim_weather -->|JOIN| exec
    dim_holiday -->|JOIN| exec
    dim_area -->|JOIN| exec
    fact_trip -->|Dataform SQL| bi1
    fact_trip -->|Dataform SQL| bi2
    fact_trip -->|Dataform SQL| fc_feat
    fact_trip -->|Dataform SQL| tips
    fact_daily -->|Dataform SQL| hw
    fact_daily -->|Dataform SQL| fc_dash

    fact_daily ==>|Python: train.py\nreads from BQ| train
    train -->|saves .pkl| predict
    fact_daily ==>|Python: predict.py\nreads from BQ| predict
    predict -->|saves CSV| upload
    upload ==>|Python: load_table\nWRITE_TRUNCATE| preds
    preds ==>|Dataform: LEFT JOIN\nforecast_dashboard.sqlx| fc_dash

    bi2 -->|BigQuery connector| looker
    over -->|BigQuery connector| looker
    tips -->|BigQuery connector| looker
    fc_dash -->|BigQuery connector| looker

    classDef src fill:#fafafa,stroke:#9e9e9e,color:#424242
    classDef ing fill:#fff3e0,stroke:#e65100,color:#bf360c
    classDef bronze fill:#ffe0b2,stroke:#e65100,color:#bf360c
    classDef silver fill:#c5cae9,stroke:#283593,color:#1a237e
    classDef asrt fill:#fff8e1,stroke:#f9a825,color:#f57f17
    classDef goldDim fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    classDef goldFact fill:#fff9c4,stroke:#f57f17,color:#e65100
    classDef goldShift fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    classDef goldRpt fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef ml fill:#fce4ec,stroke:#c2185b,color:#880e4f
    classDef bi fill:#f5f5f5,stroke:#616161,color:#212121

    class pub,weather_api,holiday_api src
    class fetch_w,fetch_h ing
    class raw_taxi,raw_weather,raw_holidays bronze
    class stg_taxi,stg_weather,stg_holidays silver
    class asrt_taxi,asrt_weather,asrt_holiday asrt
    class dim_date,dim_weather,dim_holiday,dim_area goldDim
    class fact_trip,fact_daily goldFact
    class vad,over goldShift
    class exec,hw,bi1,bi2,geo,fc_feat,fc_dash,tips goldRpt
    class train,predict,upload,preds ml
    class looker bi