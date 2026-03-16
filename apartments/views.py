from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson.objectid import ObjectId
from .db import apartments_collection, users_collection, deposit_orders_collection, viewing_appointments_collection, projects_collection

def serialize_doc(doc):
    """Helper to convert MongoDB document to JSON serializable format."""
    if not doc:
        return None
    if '_id' in doc:
        doc['id'] = str(doc.pop('_id'))
    return doc

class ApartmentListCreateView(APIView):
    def get(self, request):
        """List all apartments."""
        try:
            apartments = list(apartments_collection.find())
            serialized_apartments = [serialize_doc(apt) for apt in apartments]
            return Response(serialized_apartments, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Create a new apartment."""
        try:
            data = request.data
            result = apartments_collection.insert_one(data)
            created_apartment = apartments_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_apartment), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApartmentDetailView(APIView):
    def get(self, request, pk):
        """Retrieve an apartment by id."""
        try:
            apartment = apartments_collection.find_one({"_id": ObjectId(pk)})
            if not apartment:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_doc(apartment), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """Update an apartment by id."""
        try:
            data = request.data
            # We should not update the _id field
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            result = apartments_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": data}
            )
            
            if result.matched_count == 0:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)
                
            updated_apartment = apartments_collection.find_one({"_id": ObjectId(pk)})
            return Response(serialize_doc(updated_apartment), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete an apartment by id."""
        try:
            result = apartments_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

class ProjectListCreateView(APIView):
    def get(self, request):
        try:
            items = list(projects_collection.find())
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            result = projects_collection.insert_one(data)
            created_item = projects_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_item), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProjectDetailView(APIView):
    def get(self, request, pk):
        try:
            item = projects_collection.find_one({"_id": ObjectId(pk)})
            if not item:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_doc(item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            data = request.data
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            result = projects_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": data}
            )
            
            if result.matched_count == 0:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
                
            updated_item = projects_collection.find_one({"_id": ObjectId(pk)})
            return Response(serialize_doc(updated_item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = projects_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

class UserListCreateView(APIView):
    def get(self, request):
        try:
            items = list(users_collection.find())
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            result = users_collection.insert_one(data)
            created_item = users_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_item), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserDetailView(APIView):
    def get(self, request, pk):
        try:
            item = users_collection.find_one({"_id": ObjectId(pk)})
            if not item:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_doc(item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            data = request.data
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            result = users_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": data}
            )
            
            if result.matched_count == 0:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
            updated_item = users_collection.find_one({"_id": ObjectId(pk)})
            return Response(serialize_doc(updated_item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = users_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

class DepositOrderListCreateView(APIView):
    def get(self, request):
        try:
            items = list(deposit_orders_collection.find())
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            result = deposit_orders_collection.insert_one(data)
            created_item = deposit_orders_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_item), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DepositOrderDetailView(APIView):
    def get(self, request, pk):
        try:
            item = deposit_orders_collection.find_one({"_id": ObjectId(pk)})
            if not item:
                return Response({"error": "DepositOrder not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_doc(item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            data = request.data
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            result = deposit_orders_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": data}
            )
            
            if result.matched_count == 0:
                return Response({"error": "DepositOrder not found"}, status=status.HTTP_404_NOT_FOUND)
                
            updated_item = deposit_orders_collection.find_one({"_id": ObjectId(pk)})
            return Response(serialize_doc(updated_item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = deposit_orders_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "DepositOrder not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

class ViewingAppointmentListCreateView(APIView):
    def get(self, request):
        try:
            items = list(viewing_appointments_collection.find())
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            result = viewing_appointments_collection.insert_one(data)
            created_item = viewing_appointments_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_item), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ViewingAppointmentDetailView(APIView):
    def get(self, request, pk):
        try:
            item = viewing_appointments_collection.find_one({"_id": ObjectId(pk)})
            if not item:
                return Response({"error": "ViewingAppointment not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_doc(item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            data = request.data
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            result = viewing_appointments_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": data}
            )
            
            if result.matched_count == 0:
                return Response({"error": "ViewingAppointment not found"}, status=status.HTTP_404_NOT_FOUND)
                
            updated_item = viewing_appointments_collection.find_one({"_id": ObjectId(pk)})
            return Response(serialize_doc(updated_item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = viewing_appointments_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "ViewingAppointment not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)
