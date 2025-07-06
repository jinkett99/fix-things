# The Love for fixing things
*An Operations Research Case Study on a Hospital ED System*

**Project Timeline (Marked completion date: 8 July 2025):**
- Baseline simulations (*For Fast-Track workflow) done✅
- [Before designing full simulation] Look through past projects✅
- [Before designing full simulation] Refine "types" of simulation outputs - From past projects.✅
- [While designing full simulation] Add complexity of integrating BOTH (1) Fast-Track & (2) Main ED workflows to "simulation logic".✅
- [Finalise code] main.py file for PoC + README.md instructions✅
- [Report writing] Medium Article to present workflows, code, results and conclusions - *Review! ++Process Flow + neccessary tables.

![Image](images/ED.png)

---

## **Setup Instructions**  

Follow these steps in the specified order to run the scripts successfully:

### **1. Clone the Repository**  
```bash
git clone https://github.com/jinkett99/fix-things
cd fix-things
```

### **2. Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **3. Run Simulation (to model ED operations)**
```bash
python main.py
```
Additional: To customise resource & environment settings:
```bash
python main.py \
  --fast_doctors 2 \
  --fast_nurses 2 \
  --ed_doctors 4 \
  --ed_nurses 3 \
  --beds 6 \
  --n_patients 150 \
  --sim_time 1200 \
  --arrival_rate 8
```

### 🔧 **Command-Line Arguments**
| Argument         | Description                         | Default |
| ---------------- | ----------------------------------- | ------- |
| `--fast_doctors` | Number of fast-track doctors        | `1`     |
| `--fast_nurses`  | Number of fast-track nurses         | `1`     |
| `--ed_doctors`   | Number of main ED doctors           | `3`     |
| `--ed_nurses`    | Number of main ED nurses            | `2`     |
| `--beds`         | Number of ED admission beds         | `5`     |
| `--n_patients`   | Number of patients to simulate      | `100`   |
| `--sim_time`     | Total simulation time in minutes    | `1000`  |
| `--arrival_rate` | Mean interarrival time (in minutes) | `10`    |

### 📤 **Output Format**
After the simulation runs, the following outputs are generated:

- **Console Summary**:
  - Average and maximum wait times (in minutes and seconds)
  - Queue length summary (fast-track and main ED)
  - Resource utilization summary (doctors, nurses, beds)

- **Output Folder: `plots/`**
  - `queue_and_staff_utilization.png`  
    ➤ Shows queue length, doctor, and nurse utilization over time
  - `bed_utilization.png`  
    ➤ Shows ED admission bed utilization separately

> ℹ️ If not already present, the script will automatically create the `plots/` directory.

## **Content**
```
main folder/
├── 1.01-jk-experiments.ipynb           # Experimentation with discrete event simulation with simPy library. Project framing, formulation & brainstorming
├── 2.01-jk-implementation.ipynb        # Implementation of full system workflow to model performance of ED System set-up to understand system efficieny and patient experience
├── main.py                             # Python script to simulate process flow and return outputs as actionable insights (refer to output format above)
```

## **Contributing**  
Feel free to open issues and submit pull requests. Contributions are welcome!