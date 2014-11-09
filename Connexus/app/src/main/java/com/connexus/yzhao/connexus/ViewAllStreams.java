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


public class ViewAllStreams extends Activity {

    private AsyncHttpClient httpClient = new AsyncHttpClient();
    private GridView gridView;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_all_streams);

        final Button buttonSearch = (Button) findViewById(R.id.search);
        final Button buttonMySubscribedStreams = (Button) findViewById(R.id.mySubscribedStreams);
        final ImageButton nearBy = (ImageButton) findViewById(R.id.nearByStreams);

        gridView = (GridView) findViewById(R.id.gridView);
        final String[] streams = new String[16];
        final String[] strNames = new String[16];
        GridViewAdapter adapter = new GridViewAdapter(ViewAllStreams.this, streams, strNames);
        gridView.setAdapter(adapter);
        gridView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent viewSingleStreams = new Intent(ViewAllStreams.this, ViewSingleStreams.class);
                viewSingleStreams.putExtra("strPos", Integer.toString(position));
                viewSingleStreams.putExtra("strName", strNames[position]);
                ViewAllStreams.this.startActivity(viewSingleStreams);
            }
        });

        // Search
        buttonSearch.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewSearchedStreams = new Intent(ViewAllStreams.this, SearchResult.class);
                ViewAllStreams.this.startActivity(viewSearchedStreams);
            }
        });

        // Jump to MySubscribedStreams
        buttonMySubscribedStreams.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewSubscribedStreams = new Intent(ViewAllStreams.this, MySubscribedStreams.class);
                ViewAllStreams.this.startActivity(viewSubscribedStreams);
            }
        });

        // Jump to ViewNearbyStreams
        nearBy.setOnClickListener(new OnClickListener(){
            @Override
            public void onClick(View v){
                Intent viewNearbyStreams = new Intent(ViewAllStreams.this, ViewNearbyStreams.class);
                ViewAllStreams.this.startActivity(viewNearbyStreams);
            }
        });
    }

}