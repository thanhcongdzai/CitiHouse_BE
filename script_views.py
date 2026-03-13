# Generate new views

# New collections
db_mapping = {
    "users": {
        "collection": "users_collection",
        "name": "User"
    },
    "deposit_orders": {
        "collection": "deposit_orders_collection",
        "name": "DepositOrder"
    },
    "viewing_appointments": {
        "collection": "viewing_appointments_collection",
        "name": "ViewingAppointment"
    }
}

template = """
class {name}ListCreateView(APIView):
    def get(self, request):
        try:
            items = list({collection}.find())
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({{"error": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            result = {collection}.insert_one(data)
            created_item = {collection}.find_one({{"_id": result.inserted_id}})
            return Response(serialize_doc(created_item), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({{"error": str(e)}}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class {name}DetailView(APIView):
    def get(self, request, pk):
        try:
            item = {collection}.find_one({{"_id": ObjectId(pk)}})
            if not item:
                return Response({{"error": "{name} not found"}}, status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_doc(item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({{"error": "Invalid ID format or server error"}}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            data = request.data
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            result = {collection}.update_one(
                {{"_id": ObjectId(pk)}},
                {{"$set": data}}
            )
            
            if result.matched_count == 0:
                return Response({{"error": "{name} not found"}}, status=status.HTTP_404_NOT_FOUND)
                
            updated_item = {collection}.find_one({{"_id": ObjectId(pk)}})
            return Response(serialize_doc(updated_item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({{"error": str(e)}}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = {collection}.delete_one({{"_id": ObjectId(pk)}})
            if result.deleted_count == 0:
                return Response({{"error": "{name} not found"}}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({{"error": "Invalid ID format or server error"}}, status=status.HTTP_400_BAD_REQUEST)
"""

with open("append_views.txt", "w") as f:
    for key, val in db_mapping.items():
        f.write(template.format(name=val['name'], collection=val['collection']))
