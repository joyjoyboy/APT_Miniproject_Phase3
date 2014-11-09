package com.connexus.yzhao.connexus;

import android.content.Intent;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.GridView;


public class SearchResult extends ActionBarActivity {

    private GridView gridView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search_result);

        final Button buttonSearch = (Button) findViewById(R.id.search);
        final Button buttonMoreRes = (Button) findViewById(R.id.moreRes);
        final Button buttonStreams = (Button) findViewById(R.id.streams);

        gridView = (GridView) findViewById(R.id.gridView);
        final String[] streams = new String[8];
        final String[] strNames = new String[8];
        SearchAdapter adapter = new SearchAdapter(SearchResult.this, streams, strNames);
        gridView.setAdapter(adapter);
        gridView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                Intent viewSingleStreams = new Intent(SearchResult.this, ViewSingleStreams.class);
                viewSingleStreams.putExtra("strPos", Integer.toString(position));
                viewSingleStreams.putExtra("strName", strNames[position]);
                SearchResult.this.startActivity(viewSingleStreams);
            }
        });

        buttonSearch.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

            }
        });

        buttonMoreRes.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

            }
        });

        // Jump to all streams
        buttonStreams.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewAllStreams = new Intent(SearchResult.this, ViewAllStreams.class);
                SearchResult.this.startActivity(viewAllStreams);
            }
        });
    }

}
