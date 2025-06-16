# Transforming Unstructured Data into Structured Using AI

[![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27200%27%20height=%27200%27/%3e)![Martyna Slawinska's photo](https://mindsdb.com/blog/_next/image?url=https%3A%2F%2Fcdn.hashnode.com%2Fres%2Fhashnode%2Fimage%2Fupload%2Fv1701795693260%2FOa1qyierU.png%3Fw%3D200%26h%3D200%26fit%3Dcrop%26crop%3Dfaces%26auto%3Dcompress%2Cformat%26format%3Dwebp&w=640&q=75)](https://hashnode.com/@martyna)

[Martyna Slawinska](https://hashnode.com/@martyna)

·Nov 22, 2024·

![Cover Image for Transforming Unstructured Data into Structured Using AI](https://cdn.hashnode.com/res/hashnode/image/upload/v1732286295221/6873cfdf-9aed-41dc-9351-178434280dea.jpeg?w=1600&h=840&fit=crop&crop=entropy&auto=compress,format&format=webp)

In this digital age, the vast majority of data generated is unstructured, ranging from emails and social media posts to audio and video content. This presents a significant challenge for organizations seeking to harness this data for insights and decision-making. Leveraging artificial intelligence (AI) to structure unstructured data is crucial, as AI can process and analyze large volumes of data quickly and accurately.

Traditional methods for structuring unstructured data involve manual processes or rule-based systems, which can be time-consuming, error-prone, and difficult to scale. While these methods can provide some level of organization, they lack the efficiency and adaptability of AI-powered solutions. AI, or specifically large language models (LLMs), simplifies the process of extracting relevant information from unstructured data. This accelerates data processing and enhances accuracy, enabling real-time data analysis.

One notable solution in this space is provided by [MindsDB](https://mindsdb.com/), an open source AI platform that brings structured and unstructured data together for enterprise AI. The solution utilizes MindsDB's integration with Large Language Models to extract relevant data from unstructured text and insert it into a database. This way you can convert large amounts of unstructured data into structured formats using only a few SQL commands. Read along to follow the tutorial.

## Tutorial

Start by setting up MindsDB locally via [Docker](https://docs.mindsdb.com/setup/self-hosted/docker) or [Docker Desktop](https://docs.mindsdb.com/setup/self-hosted/docker-desktop).

Connect your data source that contains unstructured data to MindsDB. [See all supported data sources here](https://docs.mindsdb.com/integrations/data-overview).

In this example, we use the sample data containing property descriptions as follows.

We have unstructured data in the form of property descriptions that contain details about properties such as address, square footage, and number of bedrooms and bathrooms.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732290050350/04b54d98-c22a-4630-98d8-4b8c8a746c6f.png?auto=compress,format&format=webp)

We want to extract relevant data from descriptions and store it in another table. To do that we use the [OpenAI model with the JSON Extract feature](https://docs.mindsdb.com/use-cases/data_enrichment/json-from-text).

Firstly, we create an OpenAI engine providing the OpenAI API key.

```
CREATE ML_ENGINE openai_engine
FROM openai
USING
    openai_api_key = 'your-openai-api-key';
```

Secondly, we create an AI model to extract relevant data values from descriptions.

```
CREATE MODEL extract_data_model
PREDICT json
USING
    engine = 'openai_engine',
    json_struct = {
        'nobath': 'number of bathrooms',
        'nobed': 'number of bedrooms',
        'sqft': 'square footage of the property (only integer)',
        'address': 'address includes house number and street name',
        'city': 'city',
        'zipcode': 'zipcode includes two letters (state) and five digits',
        'country': 'country'
    },
    prompt_template = '{{description}}';
```

The _json_struct_ parameter stores data fields and their descriptions; these data fields will be extracted from unstructured data. MindsDB has custom-implemented it to ease the process of extracting desired data from unstructured volumes of data.

The _prompt_template_ parameter stores the column name that contains property descriptions in double curly braces, which will be replaced by property descriptions from the input data upon joining the model with the input data.

```
SELECT d.description, m.json
FROM data_source.property AS d
JOIN extract_data_model AS m;
```

Here is the output:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732289982068/3b9fcb8b-3854-4d0b-a4dc-009664563d15.png?auto=compress,format&format=webp)

Now that we have extracted relevant data from descriptions into JSON format, we can insert it into another table.

```
INSERT INTO data_source.property_details
SELECT json_extract(json, '$.address') AS address,
           json_extract(json, '$.city') AS city,
           json_extract(json, '$.country') AS country,
           json_extract(json, '$.zipcode') AS zipcode,
           json_extract(json, '$.sqft') AS sqft,
           json_extract(json, '$.nobed') AS nobed,
           json_extract(json, '$.nobath') AS nobath
 FROM (SELECT m.json
          FROM data_source.property AS d
          JOIN extract_data_model AS m);
```

Here is the resulting table:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1732290080156/6168622b-203a-48fc-abdc-10962d23d78b.png?auto=compress,format&format=webp)

You can adapt this tutorial to your use case by modifying the _json_struct_ parameter value when creating the model, which allows you to specify what data should be extracted from the given unstructured data.

## Automating Data Structuring for Newly Added Unstructured Data

With MindsDB, you can automate the transformation of newly added unstructured data into a structured format. Setting up a job ensures that every time new data becomes available, it is automatically processed and stored in the desired format.

```
CREATE JOB structure_data (
INSERT INTO data_source.property_details
    SELECT json_extract(json, '$.address') AS address,
           json_extract(json, '$.city') AS city,
           json_extract(json, '$.country') AS country,
           json_extract(json, '$.zipcode') AS zipcode,
           json_extract(json, '$.sqft') AS sqft,
           json_extract(json, '$.nobed') AS nobed,
           json_extract(json, '$.nobath') AS nobath
    FROM (SELECT m.json
          FROM data_source.property AS d
          JOIN extract_data_model AS m
          WHERE d.id > LAST)
)
```

This job, upon its execution, transforms new loads of unstructured data into the defined format and inserts it into a data table.

This is a conditional job that attempts its execution _EVERY 1 day_ but actually executes the _INSERT INTO_ statement only _IF_ there is new data available in the _property_ table. The _LAST_ keyword used in the _WHERE_ clause checks if any new data has been added since the last check. If new data has been added, then the query inside the _IF_ clause returns data, and subsequently, the _INSERT INTO_ statement is executed.

The key benefits of this approach include:

- Efficiency: It automates routine data transformation tasks.
    
- Conditional Execution: It avoids unnecessary processing by executing only when new data is available.
    
- Seamless Integration: It ensures that structured data tables stay up-to-date without manual intervention.
    

Note that conditional jobs can serve a multitude of different use cases. Check out more [use cases of MindsDB here](https://docs.mindsdb.com/use-cases/overview).

## Conclusion

Transforming unstructured data into valuable insights doesn’t have to be complex. With MindsDB, you can quickly extract desired details from text using just a few simple SQL commands – making the process fast and straightforward. It’s also highly adaptable: customize the json_struct settings to align perfectly with your data requirements.