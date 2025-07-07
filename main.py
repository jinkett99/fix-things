import os
import simpy
import numpy as np
import random
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

# ------------------- Hospital Class ------------------- #
class Hospital:
    def __init__(self, env, fast_doctors, fast_nurses, ed_doctors, ed_nurses, beds):
        self.env = env
        self.fast_doctor = simpy.Resource(env, fast_doctors)
        self.fast_nurse = simpy.Resource(env, fast_nurses)
        self.ed_doctor = simpy.Resource(env, ed_doctors)
        self.ed_nurse = simpy.Resource(env, ed_nurses)
        self.beds = simpy.Resource(env, beds)

    def consult(self):
        yield self.env.timeout(max(5, np.random.normal(20, 5)))

    def medication(self):
        yield self.env.timeout(max(5, np.random.normal(15, 3)))

    def review(self):
        yield self.env.timeout(max(3, np.random.normal(10, 3)))

    def admit(self):
        yield self.env.timeout(max(5, np.random.normal(30, 5)))

    def fast_lab(self):
        yield self.env.timeout(max(1, np.random.normal(6, 3)))
    
    def fast_lab_wait(self):
        yield self.env.timeout(max(10, np.random.normal(25, 5)))

    def ed_lab_wait(self):
        yield self.env.timeout(max(15, np.random.normal(40, 10)))

    def ed_lab(self):
        yield self.env.timeout(max(3, np.random.normal(10, 4)))


# ------------------- Patient Process ------------------- #
def patient(env, name, hospital, wait_times):
    arrival_time = env.now
    is_fast_track = random.random() < 0.3

    if is_fast_track:
        with hospital.fast_doctor.request() as req:
            yield req
            yield env.process(hospital.consult())

        if random.random() < 0.3:
            with hospital.fast_nurse.request() as req:
                yield req
                yield env.process(hospital.fast_lab())
            yield env.process(hospital.fast_lab_wait())
            with hospital.fast_doctor.request() as req:
                yield req
                yield env.process(hospital.review())

        with hospital.fast_nurse.request() as req:
            yield req
            yield env.process(hospital.medication())

    else:
        with hospital.ed_doctor.request() as req:
            yield req
            yield env.process(hospital.consult())

        if random.random() < 0.7:
            with hospital.ed_nurse.request() as req:
                yield req
                yield env.process(hospital.ed_lab())
            yield env.process(hospital.ed_lab_wait())
            with hospital.ed_doctor.request() as req:
                yield req
                yield env.process(hospital.review())

        if random.random() < 0.5:
            with hospital.beds.request() as req:
                yield req
                yield env.process(hospital.admit())
        else:
            with hospital.ed_nurse.request() as req:
                yield req
                yield env.process(hospital.medication())

    wait_times.append(env.now - arrival_time)


# ------------------- Monitoring ------------------- #
def monitor(env, hospital, metrics, interval=5):
    while True:
        metrics['timeline'].append(env.now)
        metrics['queue_fast'].append(len(hospital.fast_doctor.queue) + len(hospital.fast_nurse.queue))
        metrics['queue_ed'].append(len(hospital.ed_doctor.queue) + len(hospital.ed_nurse.queue))

        metrics['util_fast_doc'].append(hospital.fast_doctor.count / hospital.fast_doctor.capacity)
        metrics['util_fast_nurse'].append(hospital.fast_nurse.count / hospital.fast_nurse.capacity)
        metrics['util_ed_doc'].append(hospital.ed_doctor.count / hospital.ed_doctor.capacity)
        metrics['util_ed_nurse'].append(hospital.ed_nurse.count / hospital.ed_nurse.capacity)
        metrics['util_beds'].append(hospital.beds.count / hospital.beds.capacity)

        yield env.timeout(interval)


# ------------------- Reporting ------------------- #
def report(wait_times, metrics):
    avg_wait = np.mean(wait_times)
    max_wait = np.max(wait_times)

    print("=== Simulation Results ===")
    print(f"Average Wait Time: {int(avg_wait)} min")
    print(f"Max Wait Time:     {int(max_wait)} min\n")

    print("--- Average Queue Lengths ---")
    queue_data = [
        ["Fast-Track Queue", f"{np.mean(metrics['queue_fast']):.2f}"],
        ["Main ED Queue", f"{np.mean(metrics['queue_ed']):.2f}"]
    ]
    print(tabulate(queue_data, headers=["Queue Type", "Avg Length"], tablefmt="github"))
    print()

    # Summary Table
    summary_data = [
        ["Fast-Track Doctor Util", f"{100 * np.mean(metrics['util_fast_doc']):.2f}%"],
        ["Fast-Track Nurse Util", f"{100 * np.mean(metrics['util_fast_nurse']):.2f}%"],
        ["Main ED Doctor Util", f"{100 * np.mean(metrics['util_ed_doc']):.2f}%"],
        ["Main ED Nurse Util", f"{100 * np.mean(metrics['util_ed_nurse']):.2f}%"],
        ["Bed Utilization", f"{100 * np.mean(metrics['util_beds']):.2f}%"]
    ]
    print("--- Resource Utilization Summary ---")
    print(tabulate(summary_data, headers=["Resource", "Avg Utilization"], tablefmt="github"))

    # Create output directory
    os.makedirs("plots", exist_ok=True)

    # Plot 1: Queue Lengths and Utilization (Doctors and Nurses)
    plt.figure(figsize=(14, 10))

    plt.subplot(3, 1, 1)
    plt.plot(metrics['timeline'], metrics['queue_fast'], label='Fast-Track Queue')
    plt.plot(metrics['timeline'], metrics['queue_ed'], label='Main ED Queue')
    plt.title('Queue Lengths Over Time')
    plt.xlabel('Time (min)')
    plt.ylabel('Queue Length')
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(metrics['timeline'], metrics['util_fast_doc'], label='Fast-Track Doctor')
    plt.plot(metrics['timeline'], metrics['util_ed_doc'], label='Main ED Doctor')
    plt.title('Doctor Utilization Over Time')
    plt.xlabel('Time (min)')
    plt.ylabel('Utilization (0-1)')
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 3)
    plt.plot(metrics['timeline'], metrics['util_fast_nurse'], label='Fast-Track Nurse')
    plt.plot(metrics['timeline'], metrics['util_ed_nurse'], label='Main ED Nurse')
    plt.title('Nurse Utilization Over Time')
    plt.xlabel('Time (min)')
    plt.ylabel('Utilization (0-1)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("plots/queue_and_staff_utilization.png")
    plt.close()

    # Plot 2: Bed Utilization
    plt.figure(figsize=(8, 4))
    plt.plot(metrics['timeline'], metrics['util_beds'], label='Bed Utilization', color='brown')
    plt.title('Admission Bed Utilization Over Time')
    plt.xlabel('Time (min)')
    plt.ylabel('Utilization (0-1)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("plots/bed_utilization.png")
    plt.close()


# ------------------- Main ------------------- #
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fast_doctors', type=int, default=1)
    parser.add_argument('--fast_nurses', type=int, default=1)
    parser.add_argument('--ed_doctors', type=int, default=5)
    parser.add_argument('--ed_nurses', type=int, default=5)
    parser.add_argument('--beds', type=int, default=5)
    parser.add_argument('--n_patients', type=int, default=144)
    parser.add_argument('--sim_time', type=int, default=1440)
    parser.add_argument('--arrival_rate', type=float, default=10)
    args = parser.parse_args()

    random.seed(42)
    np.random.seed(42)

    env = simpy.Environment()
    hospital = Hospital(env, args.fast_doctors, args.fast_nurses, args.ed_doctors, args.ed_nurses, args.beds)

    wait_times = []
    metrics = defaultdict(list)

    def patient_generator():
        for i in range(args.n_patients):
            env.process(patient(env, f"Patient {i+1}", hospital, wait_times))
            yield env.timeout(np.random.exponential(args.arrival_rate))

    env.process(patient_generator())
    env.process(monitor(env, hospital, metrics))
    env.run(until=args.sim_time)

    report(wait_times, metrics)


if __name__ == '__main__':
    main()
