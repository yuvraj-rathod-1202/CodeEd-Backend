from app.models.BaseModel.personalized.personal import Personalized_Flowchart, Personalized_Flowchart_Content
from typing import List

def extract_personalized_flowchart(flowchart_data) -> Personalized_Flowchart:
    return Personalized_Flowchart(
        title=flowchart_data.get('title', ''),
        feedback=flowchart_data.get('feedback', ''),
        node_count=len(flowchart_data.get('nodes', []))
    )

class FlowchartService:
    def __init__(self, db):
        self.db = db

    def get_last5_flowcharts(self, userId: str) -> Personalized_Flowchart_Content:
        flowchart_docs = self.db.collection('users').document(userId).collection('flowcharts').get()
        if not flowchart_docs:
            return Personalized_Flowchart_Content(flowcharts=[])

        flowcharts = [flowchart_doc.to_dict() for flowchart_doc in flowchart_docs]
        # Sort flowcharts by generatedAt in descending order and get the last 5
        sorted_flowcharts = sorted(flowcharts, key=lambda x: x['generatedAt'], reverse=True)[:5]
        flowcharts = []
        for flowchart in sorted_flowcharts:
            flowcharts.append(extract_personalized_flowchart(flowchart))
        return Personalized_Flowchart_Content(flowcharts=flowcharts)