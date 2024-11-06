from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import random
import pandas as pd

# Donor Agent class
class Donor(Agent):
    def __init__(self, unique_id, model, donor_data):
        super().__init__(unique_id, model)
        self.donor_data = donor_data
        self.knn_score = donor_data.get('knn_score', 0)
        self.is_donor = False
        self.call_count = 0
        self.donation = 0

    def step(self):
        if self.decide_to_donate():
            charities = [agent for agent in self.model.schedule.agents if isinstance(agent, Charity)]
            if charities:
                charity = random.choice(charities)
                self.donate(charity)

    def decide_to_donate(self):
        return self.call_count < 3 and self.donor_data['RECENT_RESPONSE_COUNT'] > 3

    def donate(self,charity):
        self.donation = random.uniform(0.01, 0.99) * 100
        self.model.total_donation += self.donation
        self.is_donor = True
        self.call_count += 1

        self.model.interactions.append({
            'source': self.unique_id,
            'target': charity.unique_id,
            'amount': self.donation
        })

# Charity Agent class
class Charity(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        donors = [agent for agent in self.model.schedule.agents if isinstance(agent, Donor)]
        top_donors = sorted(donors, key=lambda d: d.knn_score, reverse=True)[:10]
        for donor in top_donors:
            self.call_donor(donor)

    def call_donor(self, donor):
        donor.call_count += 1
        if donor.decide_to_donate():
            donor.donate(self)

# Main model class
class DonationModel(Model):
    def __init__(self, num_donors, num_charities, donor_data_df):
        self.num_donors = num_donors
        self.num_charities = num_charities
        self.grid = MultiGrid(10, 10, True)
        self.schedule = RandomActivation(self)
        self.total_donation = 0
        self.donation_history = []
        self.interactions = [] 

        # Data collector to track total donations
        self.datacollector = DataCollector(
            model_reporters={"Total Donations": lambda m: m.total_donation}
        )

        # Use the passed DataFrame
        self.donor_data = donor_data_df
        self.knn_classifier = self.train_knn(self.donor_data)

        # Create donor agents
        for i in range(self.num_donors):
            donor_data = self.donor_data.iloc[i].to_dict()
            donor = Donor(i, self, donor_data)
            self.schedule.add(donor)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(donor, (x, y))

        # Create charity agents
        for j in range(self.num_charities):
            charity = Charity(j + self.num_donors, self)
            self.schedule.add(charity)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(charity, (x, y))

        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        self.donation_history.append(self.total_donation)
        self.datacollector.collect(self)
        self.evaluate_knn_accuracy()  # Check accuracy after each step

    def evaluate_knn_accuracy(self):
        # Use the original data for evaluation
        X = self.donor_data.drop(columns=['TARGET_B', 'TARGET_D'])
        y = self.donor_data['TARGET_B']

        encoder = OneHotEncoder()
        X_encoded = encoder.fit_transform(X)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_encoded.toarray())

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        y_pred = self.knn_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f'Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}')


    def get_agent_positions(self):
        positions = []
        for agent in self.schedule.agents:
            if isinstance(agent, Donor):
                positions.append({
                    'type': 'Donor',
                    'id': agent.unique_id,
                    'x': agent.pos[0],
                    'y': agent.pos[1],
                    'donation': agent.donation
                })
            elif isinstance(agent, Charity):
                positions.append({
                    'type': 'Charity',
                    'id': agent.unique_id,
                    'x': agent.pos[0],
                    'y': agent.pos[1]
                })
        return {'positions': positions, 'interactions': self.interactions}

    def train_knn(self, data):
        
        X = data.drop(columns=['TARGET_B', 'TARGET_D'])
        y = data['TARGET_B']

        encoder = OneHotEncoder()
        X_encoded = encoder.fit_transform(X)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_encoded.toarray())

        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        knn = KNeighborsClassifier(n_neighbors=5, metric='manhattan')
        knn.fit(X_train, y_train)

        y_pred = knn.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f'Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}')
        return knn

