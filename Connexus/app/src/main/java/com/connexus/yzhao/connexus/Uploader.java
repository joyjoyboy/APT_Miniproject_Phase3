package com.connexus.yzhao.connexus;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
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
import android.widget.TextView;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;


public class Uploader extends ActionBarActivity {

    private AsyncHttpClient httpClient = new AsyncHttpClient();

    private static final String UPLOAD_URL = "http://phase2connexus.appspot.com/androidUpload";
    private static final int TAKE_PHOTO = 1;
    private static final int CHOOSE_FROM_LIBRARY = 2;
    private ImageView imageView;
    private Bitmap selectedImg;
    private String photoPath;

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

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_uploader);

        Intent intent = getIntent();
        final String strName = intent.getStringExtra("strName");
        TextView txtView = (TextView) findViewById(R.id.streamName);
        txtView.setText("Stream: " + strName);

        imageView = (ImageView) findViewById(R.id.imageView);
        Button buttonTakePhoto = (Button) findViewById(R.id.useCamera);
        Button buttonChoosePhoto = (Button) findViewById(R.id.chooseFromLibrary);
        Button buttonUpload = (Button) findViewById(R.id.upload);

        buttonTakePhoto.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                Intent takePhotoIntent = new Intent(Uploader.this, Camera.class);
                startActivityForResult(takePhotoIntent, TAKE_PHOTO);
            }
        });

        buttonChoosePhoto.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                Intent choosePhotoIntent = new Intent(Intent.ACTION_GET_CONTENT);
                choosePhotoIntent.setType("image/*");
                startActivityForResult(Intent.createChooser(choosePhotoIntent, "CHOOSE FROM LIBRARY"), CHOOSE_FROM_LIBRARY);
            }
        });

        buttonUpload.setOnClickListener(new View.OnClickListener(){

            @Override
            public void onClick(View v){

                RequestParams params = new RequestParams();
                params.put("strName", strName);

                File f = new File(photoPath);
                try {
                    params.put("img", f);
                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                }

                httpClient.post(UPLOAD_URL, params, new AsyncHttpResponseHandler()
                {
                    @Override
                    public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                        System.out.println("Succeeded!");
                        Intent viewAllStreams = new Intent(Uploader.this, ViewAllStreams.class);
                        Uploader.this.startActivity(viewAllStreams);
                    }

                    @Override
                    public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                        System.out.println("Failed!");
                        Intent viewAllStreams = new Intent(Uploader.this, ViewAllStreams.class);
                        Uploader.this.startActivity(viewAllStreams);
                    }
                });

            }
        });
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == TAKE_PHOTO && resultCode == RESULT_OK) {
            photoPath = data.getStringExtra("PhotoPath");
            byte[] byteArr = data.getByteArrayExtra("pic");
            selectedImg = BitmapFactory.decodeByteArray(byteArr, 0, byteArr.length);
            imageView.setImageBitmap(selectedImg);
        }
        if (requestCode == CHOOSE_FROM_LIBRARY && resultCode == RESULT_OK) {
            final Uri imageUri = data.getData();
            photoPath = getPath(imageUri);
            BitmapFactory.Options options = new BitmapFactory.Options();
            options.inSampleSize = 4;
            selectedImg = BitmapFactory.decodeFile(getPath(imageUri), options);
            imageView.setImageBitmap(selectedImg);
        }
    }

}
