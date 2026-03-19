from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from bson.objectid import ObjectId
import json
import cloudinary.uploader
from .db import apartments_collection, users_collection, deposit_orders_collection, viewing_appointments_collection, projects_collection, password_resets_collection

def serialize_doc(doc):
    """Helper to convert MongoDB document to JSON serializable format."""
    if not doc:
        return None
    if '_id' in doc:
        doc['id'] = str(doc.pop('_id'))
    return doc


def extract_payload_data(request, json_key_candidates=None):
    if json_key_candidates is None:
        json_key_candidates = ["data", "payload", "apartment"]

    for key in json_key_candidates:
        raw_value = request.data.get(key)
        if raw_value is None:
            continue

        if isinstance(raw_value, dict):
            return raw_value, None

        if isinstance(raw_value, str):
            try:
                return json.loads(raw_value), None
            except json.JSONDecodeError:
                return None, f"Invalid JSON in field '{key}'"

    if hasattr(request.data, "dict"):
        data = request.data.dict()
    else:
        data = dict(request.data)

    return data, None


def upload_images_to_cloudinary(files, folder):
    urls = []
    for image_file in files:
        upload_result = cloudinary.uploader.upload(
            image_file,
            folder=folder,
            resource_type="image",
        )
        secure_url = upload_result.get("secure_url")
        if secure_url:
            urls.append(secure_url)

    return urls


def get_uploaded_files(request, keys):
    files = []
    for key in keys:
        files.extend(request.FILES.getlist(key))
    return files

class ApartmentListCreateView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

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
            data, parse_error = extract_payload_data(request)
            if parse_error:
                return Response({"error": parse_error}, status=status.HTTP_400_BAD_REQUEST)

            uploaded_files = get_uploaded_files(request, ["userImage", "userImages", "image"])
            for key in ["userImage", "userImages", "image"]:
                data.pop(key, None)

            if uploaded_files:
               image_urls = upload_images_to_cloudinary(uploaded_files, "citihouse/apartments/user-images")
               data["userImageUrl"] = ",".join(image_urls)

            result = apartments_collection.insert_one(data)
            created_apartment = apartments_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_apartment), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApartmentDetailView(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

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
            data, parse_error = extract_payload_data(request)
            if parse_error:
                return Response({"error": parse_error}, status=status.HTTP_400_BAD_REQUEST)

            # We should not update the _id field
            if '_id' in data:
                del data['_id']
            if 'id' in data:
                del data['id']

            uploaded_files = get_uploaded_files(request, ["userImage", "userImages", "image"])
            if uploaded_files:
                image_urls = upload_images_to_cloudinary(uploaded_files, "citihouse/apartments/user-images")
                data["userImageUrl"] = ",".join(image_urls)

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


class ApartmentVerifiedImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        try:
            apartment = apartments_collection.find_one({"_id": ObjectId(pk)})
            if not apartment:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)

            verified_image_url = apartment.get("verifications", {}).get("image", {}).get("verifiedImageUrl", "")
            return Response(
                {
                    "apartment_id": pk,
                    "verifiedImageUrl": verified_image_url,
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        try:
            apartment = apartments_collection.find_one({"_id": ObjectId(pk)})
            if not apartment:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)

            current_verified_image_url = apartment.get("verifications", {}).get("image", {}).get("verifiedImageUrl", "")
            if current_verified_image_url:
                return Response(
                    {"error": "verifiedImageUrl already exists. Use PUT to replace."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            uploaded_files = get_uploaded_files(request, ["verifiedImage", "verifiedImages", "image"])
            if not uploaded_files:
                return Response(
                    {"error": "Missing image file(s) in form-data key 'verifiedImage'/'verifiedImages'/'image'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            image_urls = upload_images_to_cloudinary(uploaded_files, "citihouse/apartments/verified-images")
            verified_image_url = ",".join(image_urls)

            apartments_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {"verifications.image.verifiedImageUrl": verified_image_url}},
            )

            return Response(
                {
                    "apartment_id": pk,
                    "verifiedImageUrl": verified_image_url,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            apartment = apartments_collection.find_one({"_id": ObjectId(pk)})
            if not apartment:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)

            uploaded_files = get_uploaded_files(request, ["verifiedImage", "verifiedImages", "image"])
            if not uploaded_files:
                return Response(
                    {"error": "Missing image file(s) in form-data key 'verifiedImage'/'verifiedImages'/'image'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            image_urls = upload_images_to_cloudinary(uploaded_files, "citihouse/apartments/verified-images")
            verified_image_url = ",".join(image_urls)

            apartments_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {"verifications.image.verifiedImageUrl": verified_image_url}},
            )

            return Response(
                {
                    "apartment_id": pk,
                    "verifiedImageUrl": verified_image_url,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = apartments_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {"verifications.image.verifiedImageUrl": ""}},
            )

            if result.matched_count == 0:
                return Response({"error": "Apartment not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        try:
            user = users_collection.find_one({"_id": ObjectId(pk)})
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            image_url = user.get("image")
            if not image_url:
                return Response({"error": "Image not found for this user"}, status=status.HTTP_404_NOT_FOUND)

            return Response(
                {
                    "user_id": pk,
                    "image": image_url,
                    "image_public_id": user.get("image_public_id"),
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk):
        try:
            user = users_collection.find_one({"_id": ObjectId(pk)})
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.get("image"):
                return Response(
                    {"error": "Image already exists. Use PUT to replace the image."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            image_file = request.FILES.get("image")
            if not image_file:
                return Response({"error": "Missing image file in form-data key 'image'"}, status=status.HTTP_400_BAD_REQUEST)

            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="citihouse/users",
                resource_type="image",
            )

            image_url = upload_result.get("secure_url")
            public_id = upload_result.get("public_id")

            users_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {"image": image_url, "image_public_id": public_id}},
            )

            return Response(
                {"user_id": pk, "image": image_url, "image_public_id": public_id},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            user = users_collection.find_one({"_id": ObjectId(pk)})
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            image_file = request.FILES.get("image")
            if not image_file:
                return Response({"error": "Missing image file in form-data key 'image'"}, status=status.HTTP_400_BAD_REQUEST)

            old_public_id = user.get("image_public_id")
            if old_public_id:
                cloudinary.uploader.destroy(old_public_id, resource_type="image")

            upload_result = cloudinary.uploader.upload(
                image_file,
                folder="citihouse/users",
                resource_type="image",
            )

            image_url = upload_result.get("secure_url")
            public_id = upload_result.get("public_id")

            users_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": {"image": image_url, "image_public_id": public_id}},
            )

            return Response(
                {"user_id": pk, "image": image_url, "image_public_id": public_id},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = users_collection.find_one({"_id": ObjectId(pk)})
            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            image_url = user.get("image")
            if not image_url:
                return Response({"error": "Image not found for this user"}, status=status.HTTP_404_NOT_FOUND)

            public_id = user.get("image_public_id")
            if public_id:
                cloudinary.uploader.destroy(public_id, resource_type="image")

            users_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$unset": {"image": "", "image_public_id": ""}},
            )

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

class DepositOrderByBuyerView(APIView):
    def get(self, request, buyer_id):
        """Retrieve all deposit orders by buyerID."""
        try:
            items = list(deposit_orders_collection.find({"buyerId": buyer_id}))
            if not items:
                return Response([], status=status.HTTP_200_OK)
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
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


class PasswordResetListCreateView(APIView):
    def get(self, request):
        try:
            items = list(password_resets_collection.find())
            serialized_items = [serialize_doc(item) for item in items]
            return Response(serialized_items, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            result = password_resets_collection.insert_one(data)
            created_item = password_resets_collection.find_one({"_id": result.inserted_id})
            return Response(serialize_doc(created_item), status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetDetailView(APIView):
    def get(self, request, pk):
        try:
            item = password_resets_collection.find_one({"_id": ObjectId(pk)})
            if not item:
                return Response({"error": "PasswordReset not found"}, status=status.HTTP_404_NOT_FOUND)
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

            result = password_resets_collection.update_one(
                {"_id": ObjectId(pk)},
                {"$set": data}
            )

            if result.matched_count == 0:
                return Response({"error": "PasswordReset not found"}, status=status.HTTP_404_NOT_FOUND)

            updated_item = password_resets_collection.find_one({"_id": ObjectId(pk)})
            return Response(serialize_doc(updated_item), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            result = password_resets_collection.delete_one({"_id": ObjectId(pk)})
            if result.deleted_count == 0:
                return Response({"error": "PasswordReset not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid ID format or server error"}, status=status.HTTP_400_BAD_REQUEST)
