# RoadDamage AI Engine — Mathematics Reference

This document serves as the formal reference for the mathematical formulations, optimization criteria, and geometric calculations executed inside the `ai_engine` package.

---

## 1. Damage Severity Scoring Engine

The severity scoring engine evaluates the threat level of road damages within a captured image using bounding box dimensions and class-specific threat weights.

### Variables & Constants

*   Let $N$ be the total number of detected road damage instances in the image.
*   Let $i$ be the index of a single detection, where $i \in \{1, \dots, N\}$.
*   Let $W_c$ be the severity weight assigned to class $c$:
    *   $\text{Pothole}$: $W_{\text{pothole}} = 1.0$
    *   $\text{Waterlogging}$: $W_{\text{waterlogging}} = 0.9$
    *   $\text{Alligator Crack}$: $W_{\text{alligator\_crack}} = 0.7$
    *   $\text{Longitudinal Crack}$: $W_{\text{longitudinal\_crack}} = 0.4$
    *   $\text{Transverse Crack}$: $W_{\text{transverse\_crack}} = 0.4$
*   Let $S_f$ be the scaling factor used to map normalized frame-ratio areas to standard city-grading metrics. Based on validation criteria, $S_f = 3.4$.

---

### Geometric Formulations

#### Bounding Box Area Ratio ($\text{AR}$)
Given a normalized bounding box defined by top-left coordinates $(x_{1n}, y_{1n})$ and bottom-right coordinates $(x_{2n}, y_{2n})$, where all coordinates are scaled in the range $[0.0, 1.0]$ relative to the image dimensions:

$$\text{Width Ratio} (\Delta x_n) = x_{2n} - x_{1n}$$
$$\text{Height Ratio} (\Delta y_n) = y_{2n} - y_{1n}$$

The normalized Area Ratio ($\text{AR}$) representing the proportion of the image frame covered by the bounding box is:

$$\text{AR}_i = \Delta x_{n,i} \times \Delta y_{n,i}$$

#### Total Severity Score ($S$)
The total numerical severity score $S$ is calculated by summing the weighted area ratios of all detections, multiplied by a percentage scaling factor and the scaling constant $S_f$. The final score is constrained in the range $[0, 100]$:

$$S = \min\left(100.0, \sum_{i=1}^{N} \left( \text{AR}_i \times 100.0 \times W_{c,i} \times S_f \right) \right)$$

---

### Categorical Grade Assignment
The continuous score $S$ is mapped to a three-tier municipal maintenance priority rating:

$$\text{Severity Level} = \begin{cases} 
\text{CRITICAL} & \text{if } S \ge 70.0 \\
\text{MODERATE} & \text{if } 35.0 \le S < 70.0 \\
\text{MINOR} & \text{if } S < 35.0 
\end{cases}$$

---

## 2. Real-World Execution Examples

Below are step-by-step mathematical calculations from predictions run on the `pothole_imageset` dataset.

### Example A: Minor Highway Pothole (`gettyimages-2240138615-612x612.jpg`)

*   **Detected Class:** Pothole ($W_{\text{pothole}} = 1.0$)
*   **Normalized Bounding Box Coordinates:**
    $$[x_{1n}, y_{1n}, x_{2n}, y_{2n}] = [0.3701, 0.6253, 0.7772, 0.7660]$$

#### Calculation Walkthrough:
1.  **Calculate width and height ratios:**
    $$\Delta x_n = 0.7772 - 0.3701 = 0.4071$$
    $$\Delta y_n = 0.7660 - 0.6253 = 0.1407$$
2.  **Calculate Area Ratio ($\text{AR}$):**
    $$\text{AR} = 0.4071 \times 0.1407 \approx 0.0573 \quad (5.73\% \text{ of image frame})$$
3.  **Compute Severity Score ($S$):**
    $$S = \min\left(100.0, 0.0573 \times 100.0 \times 1.0 \times 3.4 \right) = \min(100.0, 19.48) = 19.48$$
4.  **Determine Severity Level:**
    Since $19.48 < 35.0$, the severity grade is **MINOR**.

---

### Example B: Large Wet Pothole (`gettyimages-2237437347-612x612.jpg`)

*   **Detected Class:** Pothole ($W_{\text{pothole}} = 1.0$)
*   **Normalized Bounding Box Coordinates:**
    $$[x_{1n}, y_{1n}, x_{2n}, y_{2n}] = [0.0157, 0.4310, 0.8040, 0.9925]$$

#### Calculation Walkthrough:
1.  **Calculate width and height ratios:**
    $$\Delta x_n = 0.8040 - 0.0157 = 0.7883$$
    $$\Delta y_n = 0.9925 - 0.4310 = 0.5615$$
2.  **Calculate Area Ratio ($\text{AR}$):**
    $$\text{AR} = 0.7883 \times 0.5615 \approx 0.4426 \quad (44.26\% \text{ of image frame})$$
3.  **Compute Severity Score ($S$):**
    $$S = \min\left(100.0, 0.4426 \times 100.0 \times 1.0 \times 3.4 \right) = \min(100.0, 150.48) = 100.0$$
4.  **Determine Severity Level:**
    Since $100.0 \ge 70.0$, the severity grade is **CRITICAL**.
