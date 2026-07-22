from dataclasses import dataclass
from copy import deepcopy
from collections import deque
import random
import csv


@dataclass
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int

    waiting: int = 0
    turnaround: int = 0
    completion: int = 0


# =========================
# METRICS
# =========================

def calculate_metrics(processes):

    n = len(processes)

    avg_waiting = sum(p.waiting for p in processes) / n

    avg_turnaround = sum(
        p.turnaround for p in processes
    ) / n

    total_burst = sum(
        p.burst for p in processes
    )

    total_time = max(
        p.completion for p in processes
    )

    cpu_util = (
        total_burst / total_time
    ) * 100

    throughput = n / total_time

    return {

        "Average Waiting Time":
            round(avg_waiting,2),

        "Average Turnaround Time":
            round(avg_turnaround,2),

        "CPU Utilization (%)":
            round(cpu_util,2),

        "Throughput":
            round(throughput,4)

    }


# =========================
# FCFS
# =========================

def fcfs(processes):

    processes.sort(
        key=lambda p: p.arrival
    )

    time = 0

    for p in processes:

        if time < p.arrival:
            time = p.arrival

        p.waiting = time - p.arrival

        time += p.burst

        p.completion = time

        p.turnaround = (
            p.completion - p.arrival
        )

    return calculate_metrics(processes)


# =========================
# SJF
# =========================

def sjf(processes):

    completed = []

    ready = []

    time = 0

    while processes or ready:

        arriving = [

            p for p in processes

            if p.arrival <= time

        ]

        for p in arriving:

            ready.append(p)

            processes.remove(p)

        if ready:

            ready.sort(
                key=lambda p: p.burst
            )

            current = ready.pop(0)

            current.waiting = (
                time - current.arrival
            )

            time += current.burst

            current.completion = time

            current.turnaround = (
                current.completion
                - current.arrival
            )

            completed.append(current)

        else:

            time += 1

    return calculate_metrics(completed)


# =========================
# PRIORITY
# =========================

def priority_scheduling(processes):

    completed = []

    time = 0

    while len(completed) < len(processes):

        available = [

            p for p in processes

            if p.arrival <= time
            and p not in completed

        ]

        if not available:

            time += 1

            continue

        current = min(

            available,

            key=lambda p: p.priority

        )

        current.waiting = (
            time - current.arrival
        )

        time += current.burst

        current.completion = time

        current.turnaround = (
            current.completion
            - current.arrival
        )

        completed.append(current)

    return calculate_metrics(completed)


# =========================
# ROUND ROBIN
# =========================

def round_robin(
    processes,
    quantum=2
):

    queue = deque()

    visited = set()

    remaining = {

        p.pid: p.burst

        for p in processes

    }

    time = 0

    completed = 0

    total = len(processes)

    while completed < total:

        for p in processes:

            if (
                p.arrival <= time
                and p.pid not in visited
            ):

                queue.append(p)

                visited.add(p.pid)

        if not queue:

            time += 1

            continue

        current = queue.popleft()

        run_time = min(

            quantum,

            remaining[current.pid]

        )

        remaining[current.pid] -= run_time

        time += run_time

        for p in processes:

            if (
                p.arrival <= time
                and p.pid not in visited
            ):

                queue.append(p)

                visited.add(p.pid)

        if remaining[current.pid] > 0:

            queue.append(current)

        else:

            current.completion = time

            current.turnaround = (

                current.completion
                - current.arrival

            )

            current.waiting = (

                current.turnaround
                - current.burst

            )

            completed += 1

    return calculate_metrics(processes)


# =========================
# SRTF (NEW)
# =========================

def srtf(processes):

    remaining = {

        p.pid:p.burst

        for p in processes

    }

    completed = 0

    time = 0

    total = len(processes)

    while completed < total:

        available = [

            p for p in processes

            if (
                p.arrival <= time
                and remaining[p.pid] > 0
            )

        ]

        if not available:

            time += 1

            continue

        current = min(

            available,

            key=lambda p:
            remaining[p.pid]

        )

        remaining[current.pid] -= 1

        time += 1

        if remaining[current.pid] == 0:

            current.completion = time

            current.turnaround = (

                current.completion
                - current.arrival

            )

            current.waiting = (

                current.turnaround
                - current.burst

            )

            completed += 1

    return calculate_metrics(processes)


# =========================
# HRRN (NEW)
# =========================

def hrrn(processes):

    completed = []

    time = 0

    while len(completed) < len(processes):

        available = [

            p for p in processes

            if (
                p.arrival <= time
                and p not in completed
            )

        ]

        if not available:

            time += 1

            continue

        current = max(

            available,

            key=lambda p:
            (
                (time - p.arrival)
                + p.burst
            ) / p.burst

        )

        current.waiting = (
            time - current.arrival
        )

        time += current.burst

        current.completion = time

        current.turnaround = (
            current.completion
            - current.arrival
        )

        completed.append(current)

    return calculate_metrics(completed)


# =========================
# WORKLOADS
# =========================

def small_workload():

    return [

        Process("P1",0,8,3),
        Process("P2",1,4,1),
        Process("P3",2,9,4),
        Process("P4",3,5,2),
        Process("P5",4,2,5)

    ]


def medium_workload():

    processes = []

    for i in range(30):

        processes.append(

            Process(

                f"P{i+1}",

                random.randint(0,20),

                random.randint(1,20),

                random.randint(1,5)

            )

        )

    return processes


def large_workload():

    processes = []

    for i in range(100):

        processes.append(

            Process(

                f"P{i+1}",

                random.randint(0,50),

                random.randint(1,30),

                random.randint(1,5)

            )

        )

    return processes


# =========================
# CSV FILE
# =========================

with open(
    "results.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([

        "Workload",

        "Algorithm",

        "Average Waiting Time",

        "Average Turnaround Time",

        "CPU Utilization",

        "Throughput"

    ])


algorithms = {

    "FCFS": fcfs,

    "SJF": sjf,

    "Priority": priority_scheduling,

    "Round Robin": round_robin,

    "SRTF": srtf,

    "HRRN": hrrn

}

workloads = {

    "Small":
        small_workload(),

    "Medium":
        medium_workload(),

    "Large":
        large_workload()

}

for workload_name, workload in workloads.items():

    print("\n")

    print("=" * 50)

    print(workload_name)

    print("=" * 50)

    for name, algorithm in algorithms.items():

        results = algorithm(
            deepcopy(workload)
        )

        print("\n", name)

        for metric, value in results.items():

            print(metric, ":", value)

        with open(
            "results.csv",
            "a",
            newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow([

                workload_name,

                name,

                results[
                    "Average Waiting Time"
                ],

                results[
                    "Average Turnaround Time"
                ],

                results[
                    "CPU Utilization (%)"
                ],

                results[
                    "Throughput"
                ]

            ])
