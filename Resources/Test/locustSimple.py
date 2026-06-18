from locust import HttpUser, task, between
import random

ORDER_IDS = []

class OrderUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(3)
    def create_order(self):
        products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headset"]
        payload = {
            "product":  random.choice(products),
            "quantity": random.randint(1, 5),
            "price":    random.randint(50000, 500000)
        }
        with self.client.post("/order", json=payload, catch_response=True) as r:
            if r.status_code == 201:
                oid = r.json().get("order_id")
                if oid:
                    ORDER_IDS.append(oid)
                    if len(ORDER_IDS) > 5000:
                        ORDER_IDS[:] = ORDER_IDS[-5000:]
                r.success()
            else:
                r.failure(r.status_code)

    @task(4)
    def get_orders(self):
        with self.client.get("/orders", catch_response=True) as r:
            r.success() if r.status_code == 200 else r.failure(r.status_code)

    @task(2)
    def get_order_detail(self):
        if not ORDER_IDS:
            return
        oid = random.choice(ORDER_IDS)
        with self.client.get(f"/order/{oid}", catch_response=True) as r:
            r.success() if r.status_code in (200, 404) else r.failure(r.status_code)

    @task(1)
    def update_order(self):
        if not ORDER_IDS:
            return
        oid = random.choice(ORDER_IDS)
        status = random.choice(["processing", "completed", "cancelled"])
        with self.client.put(f"/order/{oid}", json={"status": status},
                             catch_response=True) as r:
            r.success() if r.status_code in (200, 404) else r.failure(r.status_code)