graph LR
    subgraph SILVER["SILVER — BigQuery + Dataform"]
        stg_taxi["stg_taxi_trips"]
        stg_weather["stg_weather"]
        stg_holidays["stg_holidays"]
    end

    subgraph DQ["DATA QUALITY CHECKPOINT — Dataform assertions"]
        asrt_taxi["7 taxi assertions<br/>dup/null unique_key<br/>positive miles, seconds, total<br/>valid timestamps<br/>bounded vehicle-day activity"]
        asrt_weather["5 weather assertions<br/>dup/null weather_date<br/>non-negative precip, snow<br/>valid temperature"]
        asrt_holiday["2 holiday assertions<br/>dup/null holiday_date"]
    end

    subgraph GOLD["GOLD — BigQuery + Dataform"]
        subgraph GD["Dimensions"]
            dim_date["dim_date"]
            dim_weather["dim_weather"]
            dim_holiday["dim_holiday"]
            dim_area["dim_chicago_community_area"]
        end
        subgraph GF["Core Facts"]
            fact_trip["fact_taxi_trip"]
            fact_daily["fact_daily_demand"]
        end
        subgraph GV["Vehicle Utilization Chain"]
            vad["vehicle_activity_day"]
            over["overworkers"]
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

    subgraph ML["ML — Python + XGBoost"]
        preds["ml.model_predictions<br/>DECLARED in Dataform"]
    end

    subgraph BI["LOOKER STUDIO"]
        looker["Dashboards"]
    end

    stg_taxi -.->|validated by| asrt_taxi
    stg_weather -.->|validated by| asrt_weather
    stg_holidays -.->|validated by| asrt_holiday

    stg_taxi --> dim_date
    stg_weather --> dim_weather
    stg_holidays --> dim_holiday

    stg_taxi --> fact_trip
    fact_trip --> fact_daily
    dim_weather --> fact_daily
    dim_holiday --> fact_daily

    stg_taxi --> vad
    vad --> over

    fact_trip --> exec
    dim_weather --> exec
    dim_holiday --> exec
    dim_area --> exec

    fact_daily --> hw

    fact_trip --> bi1
    fact_trip --> bi2
    fact_trip --> tips
    fact_trip --> fc_feat

    stg_taxi --> geo
    stg_holidays --> geo
    stg_weather --> geo
    dim_area --> geo

    fact_daily --> fc_dash
    preds -->|JOIN| fc_dash

    bi2 --> looker
    over --> looker
    tips --> looker
    fc_dash --> looker

    classDef silver fill:#c5cae9,stroke:#283593,color:#1a237e
    classDef asrt fill:#fff8e1,stroke:#f9a825,color:#f57f17
    classDef goldDim fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    classDef goldFact fill:#fff9c4,stroke:#f57f17,color:#e65100
    classDef goldShift fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c
    classDef goldRpt fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef ml fill:#fce4ec,stroke:#c2185b,color:#880e4f
    classDef bi fill:#f5f5f5,stroke:#616161,color:#212121

    class stg_taxi,stg_weather,stg_holidays silver
    class asrt_taxi,asrt_weather,asrt_holiday asrt
    class dim_date,dim_weather,dim_holiday,dim_area goldDim
    class fact_trip,fact_daily goldFact
    class vad,over goldShift
    class exec,hw,bi1,bi2,geo,fc_feat,fc_dash,tips goldRpt
    class preds ml
    class looker bi