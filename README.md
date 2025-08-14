# Auto-correct
* simple autocorrect engine that harness the famous algorithm of "minimum-edit-distance" as a building block worker
* I use the cost of adding as 1
* cost of deletion is also 1
* cost of changing the character --> a heuristic that is (sqrt of the ecludian distance on keyboard)

---
## why is this heuristic?
* normally we are most likely to get errors in nearer characters on keyboard . for example : replacing "m" with "q"  is very unlikely error

---
## some images:
<img width="563" height="349" alt="image" src="https://github.com/user-attachments/assets/5617942c-64bf-4fd9-b150-01444931fee1" />


<img width="562" height="348" alt="image" src="https://github.com/user-attachments/assets/78205469-7a5f-4a40-8f52-bf0928220c04" />


<img width="553" height="344" alt="image" src="https://github.com/user-attachments/assets/2265af48-7313-4738-8d90-c728f0e897b5" />


