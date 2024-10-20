## About Composite Indicators

A **composite indicator** combines multiple indicators into a single numerical score, allowing for a holistic assessment of complex, multi-dimensional phenomena. The purpose of a composite indicator is to offer a comprehensive, yet simplified, representation of a topic by aggregating different metrics that may reflect various aspects of the subject matter.

In general, composite indices are created using the following steps:

1. **Selecting Indicators**. Choose the most relevant indicators that represent the key dimensions of the subject.
2. **Normalization**. Ensure that indicators are comparable, typically by scaling them to a common range (e.g., 0 to 1).
3. **Weighting**. Assign weights to each indicator to reflect its relative importance within the composite score.
4. **Aggregation**. Combine the weighted indicators into a single score, often by summing or averaging.
5. **Interpretation**. Analyze and interpret the results, usually in relation to other entities (e.g., comparing countries).

### Why Use a Composite indicator?

Composite indices provide several key benefits:

- **Simplification**. They condense complex information into a single, interpretable score, making it easier to communicate results to decision-makers and stakeholders.
- **Comparability**. They allow for cross-sectional and temporal comparisons across regions, countries, or sectors.
- **Insight Generation**. By tracking changes in the indicator, policymakers, businesses, and researchers can gain insights into trends and opportunities.

---

### The DTPI: A Quarterly Digital Transformation Indicator

The **DTPI** is inspired by the **Digital Economy and Society index (DESI)** but differs in several key ways:

1. **Quarterly Updates**. Unlike DESI, which is updated annually, the DTPI provides more frequent updates—**quarterly**—to offer a more **timely pulse check** on the state of digitalization.
2. **Streamlined Structure**. While DESI tracks multiple dimensions, the DTPI focuses on **three core components** (GVA, labor demand, and employment in the ICT sector), making it more **streamlined** and **focused on economic potential**.
   
Despite being more focused, the DTPI retains the essence of DESI, centering on the economic drivers of digital transformation, but offering **more frequent insights** into how digitalization is evolving across the EU.

---

### Methodology

#### Step 1: Selection of Components

The DTPI includes three key components, each selected to represent a critical aspect of digital transformation. These components provide insights into both the economic and labor market dimensions of digitalization, allowing for a high-level assessment of a country’s digital transformation potential. The three components are:

- **Gross Value Added (GVA) in the ICT Sector**. This component measures the contribution of the **Information and Communication Technology (ICT) sector** to a country’s overall economic output, expressed as a percentage of GDP. The ICT sector is a key driver of digital transformation, encompassing industries such as telecommunications, software development, IT services, and media. The GVA in this sector reflects how much value is being created by digital activities, serving as an indicator of the sector’s role in economic growth. Higher GVA in the ICT sector implies a strong contribution of digital activities to the economy, signaling that a country is well-positioned to leverage digital technologies for further growth.

- **Labor Demand (LD) for ICT Skills**. This component captures the demand for ICT-related skills across industries by measuring the percentage of online job advertisements that require digital competencies. Labor demand for ICT skills is a direct reflection of how businesses are integrating digital technologies into their operations and seeking talent with the skills needed to support this digital transition. Strong demand for ICT skills suggests that digital transformation is progressing, as industries increasingly rely on digital tools and infrastructure. This component is crucial for identifying emerging trends in workforce needs, signaling areas of potential growth and innovation in the digital economy.

- **Employment Rate (ER) in ICT**. This component measures the employment levels in **ICT occupations**, expressed as a percentage of total employment. The ICT employment rate reflects the capacity of the labor market to absorb and sustain jobs in digital roles, such as software developers, data scientists, IT consultants, and network engineers. A higher employment rate in ICT indicates that a significant portion of the workforce is engaged in digital activities, which is an essential factor for driving and sustaining digital transformation. Countries with strong ICT employment rates are likely to have the human capital needed to support ongoing digital innovation and transformation efforts.

##### Rationale for Component Selection

These three components—GVA in ICT, labor demand for ICT skills, and employment in ICT—were chosen because together, they provide a comprehensive picture of the digital economy's health and its transformative potential. 

- **Economic Impact**: GVA in the ICT sector highlights the economic value being generated through digital activities, providing a macroeconomic perspective on the sector’s contribution to overall growth.

- **Workforce Readiness**: Labor demand for ICT skills signals how well-prepared the workforce is for the demands of a digital economy and the extent to which businesses are investing in digital capabilities.

- **Human Capital**: Employment in ICT occupations provides a measure of the availability of talent within the labor market to meet the needs of digital transformation. This is crucial for sustaining growth and innovation in the long term.

By selecting these components, the DTPI aims to capture the key elements of digital transformation that are essential for economic growth, workforce development, and the successful adoption of new technologies across industries. These factors are critical in understanding how digitalization affects both the **supply side** (economic output and workforce participation) and the **demand side** (the need for ICT skills in the market). Together, they provide a well-rounded and actionable indicator for tracking a country’s digital transformation potential.


#### Step 2: Data Collection and Smoothing

For each of the components, data is sourced from **Eurostat**, using the following datasets:

- **Gross Value Added (GVA) in the ICT Sector**: Data is collected from the **namq_10_a10** Eurostat dataset, which tracks GVA across different sectors. For the DTPI, we specifically use the data for the **ICT sector**, identified by the **NACE Rev. 2 Sector J**. Sector J refers to **"Information and Communication"**, which covers industries such as telecommunications, software development, IT services, and media. The GVA data is expressed as a percentage of GDP.
  
- **Employment Rate in ICT**: Data for employment in the ICT sector is sourced from the **namq_10_a10_e** Eurostat dataset, which includes employment by industry and sector. The employment data used is expressed as a percentage of total employment, filtered specifically for the **ICT sector (Sector J)**.

- **Labor Demand for ICT Skills**: The demand for ICT labor is measured through the **isoc_sk_oja1** dataset, which tracks online job advertisements. This dataset provides information on labor demand, specifically focusing on job postings requiring ICT skills.

- **Moving Average Smoothing**: To enhance the clarity of trends and reduce short-term fluctuations, we apply a **moving average** with a **3-quarter window** to each component (GVA, labor demand, and employment). The **window** refers to the span of consecutive data points (in this case, 3 quarters) used to calculate the average for each point in time. By averaging over this window, we smooth out temporary spikes or dips, helping to reveal the underlying trends and making the data more reliable for medium-term analysis. This smoothing process reduces noise and ensures that the indicator better reflects consistent digital transformation dynamics, rather than being influenced by short-term volatility.



#### Step 3: Data Normalization

Since the three metrics have different scales, we normalize them using **Min-Max scaling**:

$$
\text{Normalized Value} = \frac{\text{Actual Value} - \text{Minimum Value}}{\text{Maximum Value} - \text{Minimum Value}}
$$

This scaling ensures that each component is brought to a common scale (0 to 1) to make them comparable. A value of 1 indicates the highest performance in that category, and 0 indicates the lowest.

#### Step 4: Weighting the Components

The DTPI assigns **equal weights** to the three components, as each dimension is considered equally important for assessing digital transformation potential:

$$
\text{Weighting}: w_1 = w_2 = w_3 = 1
$$

This assumption may be revised in the future as more data becomes available, and different weights may be assigned depending on the sector's evolving priorities.

#### Step 5: Aggregation

The final DTPI score for each country is calculated as the **weighted average** of the normalized values of the three components:

$$
\text{DTPI} = \frac{w_1 \times \text{GVA\_normalized} + w_2 \times \text{Employment\_normalized} + w_3 \times \text{LaborDemand\_normalized}}{w_1 + w_2 + w_3}
$$

This formula aggregates the three normalized values into a single indicator score for each country, reflecting its digital transformation potential.

---

### Examples of indicator Calculation

Let’s walk through two simplified examples to better understand how DTPI scores are calculated:

#### Example 1: Country A (Low Score)

- GVA Normalized: 0.3
- Employment Normalized: 0.2
- Labor Demand Normalized: 0.1

$$
\text{DTPI}_{A} = \frac{1 \times 0.3 + 1 \times 0.2 + 1 \times 0.1}{1 + 1 + 1} = \frac{0.6}{3} = 0.2
$$

#### Example 2: Country B (High Score)

- GVA Normalized: 0.9
- Employment Normalized: 0.8
- Labor Demand Normalized: 0.85

$$
\text{DTPI}_{B} = \frac{1 \times 0.9 + 1 \times 0.8 + 1 \times 0.85}{1 + 1 + 1} = \frac{2.55}{3} = 0.85
$$

---

### Key Differences Between DTPI and 

1. **Update Frequency**. While  provides a comprehensive view of the EU's digital economy on an **annual basis**, the DTPI is updated **quarterly**, allowing for a more **dynamic assessment**.
   
2. **Focus**. DESI includes a wide range of indicators across various dimensions such as connectivity, human capital, use of internet services, and integration of digital technology. The DTPI focuses on the **economic potential** of digital transformation, streamlining the number of indicators to focus on the **economic and employment aspects** of ICT.

3. **Applicability**. DESI offers a broader scope for tracking digital society, while DTPI is more specialized in assessing **economic readiness** for digital transformation and potential growth areas.

---
### Final Remarks and Future Work

#### Justification for the Equal Weighting of Components

In the current version of the DTPI, each of the three core components—GVA, employment, and labor demand—is assigned **equal weight** (w₁ = w₂ = w₃ = 1) in the calculation of the composite indicator. This approach assumes that each component contributes equally to assessing a country's digital transformation potential. The rationale for this equal weighting is based on the importance of capturing a balanced view of economic activity, labor market conditions, and demand for ICT skills.

However, the DTPI is designed to be adaptable, and future versions may incorporate different weights based on further analysis or stakeholder input. For example, if emerging evidence shows that one component has a disproportionate impact on digital transformation, the weighting scheme could be adjusted to reflect this. 

#### Clarity on How Missing or Incomplete Data is Handled

The DTPI updates are based on the latest quarter where data for all three components (GVA, employment, and labor demand) is available. If data for any one of these components is missing for a particular quarter, the indicator is **not calculated** for that period. This ensures that the integrity of the indicator is maintained and avoids partial assessments that might distort the results. 
This approach helps to avoid skewing the indicator results and maintains consistency in tracking the digital transformation potential of countries over time.

#### Consideration of Potential Correlations Between GVA, Employment, and Labor Demand

It is important to acknowledge potential correlations between the three components of the DTPI—GVA, employment, and labor demand—when interpreting the indicator results. For example, during periods of economic growth, all three indicators may rise simultaneously, reflecting positive correlations. Conversely, labor demand for ICT skills may outpace employment growth if a skills gap exists in the market. 

The DTPI does not currently account for such interdependencies explicitly, but future iterations of the indicator may incorporate **correlation analysis** to better capture the dynamics between these components. Understanding these relationships will provide deeper insights into how different aspects of the digital economy evolve in relation to one another.

#### Future Work

1. **Dynamic Weighting**: Future versions of the DTPI may consider dynamically adjusting the weights of the three components based on their evolving relevance to digital transformation. This would allow for a more accurate reflection of the changing landscape of the digital economy.
  
2. **Correlation Analysis**: Incorporating correlation analysis between the components (GVA, employment, and labor demand) could provide deeper insights into how these factors influence one another and help to refine the indicator.

3. **Handling Missing Data**: Improving strategies for handling missing data, such as implementing more advanced imputation techniques or using alternative sources, could allow for continuous tracking even when some data is unavailable.

4. **Sector-Specific Analysis**: Future iterations could include more granular analysis by sector or industry within the ICT domain, which would provide a more detailed view of digital transformation across different economic segments.

---

### Conclusion

The **Digital Transformation Potential Indicator** offers a timely and insightful look into how countries are capitalizing on digital opportunities. By focusing on core economic metrics and providing quarterly updates, the DTPI complements existing measures like DESI while offering a more **agile and focused approach**. This enables stakeholders to stay informed about the rapid evolution of digital transformation across Europe and make **informed decisions** based on the latest data.
