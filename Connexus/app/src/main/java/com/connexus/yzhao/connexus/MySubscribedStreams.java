package com.connexus.yzhao.connexus;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.GridView;
import android.widget.ImageView;
import android.widget.ImageButton;

import android.view.View;
import android.view.View.OnClickListener;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;
import com.loopj.android.http.JsonHttpResponseHandler;
import com.loopj.android.http.RequestParams;

import org.apache.http.Header;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;


public class MySubscribedStreams extends Activity {

    private GridView gridView;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my_subscribed_streams);

        final Button buttonStreams = (Button) findViewById(R.id.streams);

        gridView = (GridView) findViewById(R.id.gridView);
        final String[] streams = new String[16];
        final String[] strNames = new String[16];
        SubscribedAdapter adapter = new SubscribedAdapter(MySubscribedStreams.this, streams, strNames);
        gridView.setAdapter(adapter);
        gridView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent viewSingleStreams = new Intent(MySubscribedStreams.this, ViewSingleStreams.class);
                viewSingleStreams.putExtra("strPos", Integer.toString(position));
                viewSingleStreams.putExtra("strName", strNames[position]);
                MySubscribedStreams.this.startActivity(viewSingleStreams);
            }
        });

        // Jump to all streams
        buttonStreams.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewAllStreams = new Intent(MySubscribedStreams.this, ViewAllStreams.class);
                MySubscribedStreams.this.startActivity(viewAllStreams);
            }
        });
    }

}