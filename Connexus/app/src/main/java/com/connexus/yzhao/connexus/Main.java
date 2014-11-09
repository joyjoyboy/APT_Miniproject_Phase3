package com.connexus.yzhao.connexus;

import android.app.Activity;
import android.content.Intent;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;


public class Main extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button buttonLogin = (Button) findViewById(R.id.userLogin);
        Button buttonViewStreams = (Button) findViewById(R.id.viewStreams);

        buttonLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewAllStreams = new Intent(Main.this, ViewAllStreams.class);
                Main.this.startActivity(viewAllStreams);
            }
        });

        buttonViewStreams.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent viewAllStreams = new Intent(Main.this, ViewAllStreams.class);
                Main.this.startActivity(viewAllStreams);
            }
        });
    }
}
