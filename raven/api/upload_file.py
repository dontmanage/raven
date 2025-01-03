import base64
import io
from mimetypes import guess_type

import dontmanage
from dontmanage import _
from dontmanage.core.doctype.file.utils import get_local_image
from dontmanage.handler import upload_file
from PIL import Image, ImageOps


def upload_JPEG_wrt_EXIF(content, filename):
	"""
	When a user uploads a JPEG file, we need to transpose the image based on the EXIF data.
	This is because the image is rotated when it is uploaded to the server.
	"""
	content_type = guess_type(filename)[0]

	# if file format is JPEG, we need to transpose the image
	if content_type.startswith("image/jpeg"):
		with Image.open(io.BytesIO(content)) as image:
			# transpose the image
			transposed_image = ImageOps.exif_transpose(image)
			#  convert the image to bytes
			buffer = io.BytesIO()
			# save the image to the buffer
			transposed_image.save(buffer, format="JPEG")
			# get the value of the buffer
			buffer = buffer.getvalue()
	else:
		buffer = base64.b64decode(content)

	return dontmanage.get_doc(
		{
			"doctype": "File",
			"file_name": filename,
			"content": buffer,
			"attached_to_doctype": "Raven Message",
			"attached_to_name": dontmanage.form_dict.docname,
			"is_private": 1,
			"attached_to_field": "file",
		}
	).insert()


@dontmanage.whitelist()
def upload_file_with_message():
	"""
	When the user uploads a file on Raven, this API is called.
	Along with the file, the user also send additional information: the channel ID
	We need to do two things:

	1. Create a Raven Message Doc
	2. Upload the file
	3. If the file is an image, we need to measure it's dimensions
	4. Store the file URL and the dimensions in the Raven Message Doc
	"""
	fileExt = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG", "gif", "GIF", "webp", "WEBP"]
	thumbnailExt = ["jpg", "JPG", "jpeg", "JPEG", "png", "PNG"]

	dontmanage.form_dict.doctype = "Raven Message"
	dontmanage.form_dict.fieldname = "file"

	message_doc = dontmanage.new_doc("Raven Message")
	message_doc.channel_id = dontmanage.form_dict.channelID
	message_doc.message_type = "File"
	message_doc.insert()

	dontmanage.form_dict.docname = message_doc.name

	# Get the files
	files = dontmanage.request.files
	# Get the file & content
	if "file" in files:
		file = files["file"]
		filename = file.filename
		"""
        If the file is a JPEG, we need to transpose the image
        Else, we need to upload the file as is
        """
		if filename.endswith(".jpeg"):
			content = file.stream.read()
			file_doc = upload_JPEG_wrt_EXIF(content, filename)
		else:
			file_doc = upload_file()

	message_doc.reload()

	message_doc.file = file_doc.file_url

	if file_doc.file_type in fileExt:

		message_doc.message_type = "Image"

		image, filename, extn = get_local_image(file_doc.file_url)
		width, height = image.size

		MAX_WIDTH = 480
		MAX_HEIGHT = 320

		# If it's a landscape image, then the thumbnail needs to be 480px wide
		if width > height:
			thumbnail_width = min(width, MAX_WIDTH)
			thumbnail_height = int(height * thumbnail_width / width)

		else:
			thumbnail_height = min(height, MAX_HEIGHT)
			thumbnail_width = int(width * thumbnail_height / height)

		# thumbnail_size = thumbnail_width, thumbnail_height

		# if extn in thumbnailExt:

		# TODO: Generate thumbnail of the image

		# Need to add a provision in DontManage to generate thumbnails for all images - not just public files
		# Generated thumbnail here throws a permissions error when trying to access.
		# thumbnail_url = f"{filename}_small.{extn}"

		# path = os.path.abspath(dontmanage.get_site_path(thumbnail_url.lstrip("/")))
		# image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

		# try:
		#     image.save(path)
		# except OSError:
		#     dontmanage.msgprint(_("Unable to write file format for {0}").format(path))
		#     thumbnail_url = file_doc.file_url

		message_doc.image_width = width
		message_doc.image_height = height
		# message_doc.file_thumbnail = thumbnail_url
		message_doc.thumbnail_width = thumbnail_width
		message_doc.thumbnail_height = thumbnail_height

	message_doc.save()

	return message_doc.name
