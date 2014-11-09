package com.connexus.yzhao.connexus;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.provider.MediaStore;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.GridView;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import org.apache.http.Header;

import java.io.File;
import java.io.IOException;
import java.util.List;


public class ViewSingleStreams extends ActionBarActivity {

    private AsyncHttpClient httpClient = new AsyncHttpClient();
    private GridView gridView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_single_streams);

        Intent intent = getIntent();
        final String strPos = intent.getStringExtra("strPos");
        final String strName = intent.getStringExtra("strName");

        TextView txtView = (TextView) findViewById(R.id.header);
        txtView.setText(strName);

        gridView = (GridView) findViewById(R.id.gridView);
        final String[] imgs = new String[16];
        SingleImageAdapter adapter = new SingleImageAdapter(ViewSingleStreams.this, imgs, strPos);
        gridView.setAdapter(adapter);
        /*
        gridView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

            }
        });
        */

        final Button buttonMorePictures = (Button) findViewById(R.id.morePictures);
        final Button buttonUploadImage = (Button) findViewById(R.id.uploadImage);
        final Button buttonStreams = (Button) findViewById(R.id.streams);

        // Display more pics
        buttonMorePictures.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

            }
        });

        // Jump to imageUploader
        buttonUploadImage.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                Intent uploadPhoto = new Intent(ViewSingleStreams.this, Uploader.class);
                uploadPhoto.putExtra("strName", strName);
                ViewSingleStreams.this.startActivity(uploadPhoto);
            }
        });

        // Jump to ViewAllStreams
        buttonStreams.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View v){
                Intent viewAllStreams = new Intent(ViewSingleStreams.this, ViewAllStreams.class);
                ViewSingleStreams.this.startActivity(viewAllStreams);
            }
        });
    }
}
