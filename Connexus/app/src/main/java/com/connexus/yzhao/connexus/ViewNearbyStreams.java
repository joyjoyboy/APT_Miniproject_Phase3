package com.connexus.yzhao.connexus;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
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

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import org.apache.http.Header;


public class ViewNearbyStreams extends ActionBarActivity {

    private GridView gridView;

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_view_nearby_streams);

        final Button buttonStreams = (Button) findViewById(R.id.streams);

        gridView = (GridView) findViewById(R.id.gridView);
        final String[] streams = new String[16];
        final String[] strNames = new String[16];
        NearByAdapter adapter = new NearByAdapter(ViewNearbyStreams.this, streams, strNames);
        gridView.setAdapter(adapter);
        gridView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent viewSingleStreams = new Intent(ViewNearbyStreams.this, ViewSingleStreams.class);
                viewSingleStreams.putExtra("strPos", Integer.toString(position));
                viewSingleStreams.putExtra("strName", strNames[position]);
                ViewNearbyStreams.this.startActivity(viewSingleStreams);
            }
        });

        // Jump to all streams
        buttonStreams.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewAllStreams = new Intent(ViewNearbyStreams.this, ViewAllStreams.class);
                ViewNearbyStreams.this.startActivity(viewAllStreams);
            }
        });
    }
}
