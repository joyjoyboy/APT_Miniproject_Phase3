package com.connexus.yzhao.connexus;

import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import com.loopj.android.http.AsyncHttpClient;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;


public class Camera extends ActionBarActivity {

    private String mCurrentPhotoPath;

    private static final int CAMERA_REQUEST = 1;
    private static final int REQUEST_TAKE_PHOTO = 2;
    private ImageView imageView;
    private Bitmap selectedImage;

    public String getPath(Uri uri) {
        if( uri == null ) {
            return null;
        }
        String[] projection = { MediaStore.Images.Media.DATA };
        Cursor cursor = managedQuery(uri, projection, null, null, null);
        if( cursor != null ){
            int column_index = cursor
                    .getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
            cursor.moveToFirst();
            return cursor.getString(column_index);
        }
        return uri.getPath();
    }

    private File createImageFile() throws IOException {
        // Create an image file name
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES);
        File image = new File(storageDir, imageFileName + ".png");
        mCurrentPhotoPath = image.getAbsolutePath();
        return image;
    }

    private void galleryAddPic() {
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        File f = new File(mCurrentPhotoPath);
        Uri contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        this.sendBroadcast(mediaScanIntent);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);

        imageView = (ImageView) findViewById(R.id.imageView);
        Button buttonTakePhoto = (Button) findViewById(R.id.takePicture);
        Button buttonUsePhoto = (Button) findViewById(R.id.usePicture);
        Button buttonStreams = (Button) findViewById(R.id.streams);

        buttonTakePhoto.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                Intent takePhotoIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                if(takePhotoIntent.resolveActivity(getPackageManager()) != null){
                    File photoFile = null;
                    try{
                        photoFile = createImageFile();
                    }catch(IOException e){
                        e.printStackTrace();
                    }
                    if(photoFile != null){
                        takePhotoIntent.putExtra(MediaStore.EXTRA_OUTPUT, Uri.fromFile(photoFile));
                        startActivityForResult(takePhotoIntent, REQUEST_TAKE_PHOTO);
                    }
                }
            }
        });

        buttonUsePhoto.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                Intent usePhotoIntent = new Intent();
                ByteArrayOutputStream stream = new ByteArrayOutputStream();
                selectedImage.compress(Bitmap.CompressFormat.PNG, 100, stream);
                byte[] byteArr = stream.toByteArray();

                usePhotoIntent.putExtra("PhotoPath", mCurrentPhotoPath);
                usePhotoIntent.putExtra("pic", byteArr);
                setResult(Camera.RESULT_OK, usePhotoIntent);
                finish();
            }
        });

        // Go back to viewAllStreams
        buttonStreams.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                Intent viewAllStreams = new Intent(Camera.this, ViewAllStreams.class);
                Camera.this.startActivity(viewAllStreams);
            }
        });
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQUEST_TAKE_PHOTO && resultCode == RESULT_OK) {

            galleryAddPic();
            File f = new File(mCurrentPhotoPath);
            final Uri imageUri = Uri.fromFile(f);
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = 4;
            selectedImage = BitmapFactory.decodeFile(getPath(imageUri), options);
            imageView.setImageBitmap(selectedImage);

        }
        if (requestCode == CAMERA_REQUEST && resultCode == RESULT_OK) {
            Bitmap photo = (Bitmap) data.getExtras().get("data");
            imageView.setImageBitmap(photo);
        }
    }
}
