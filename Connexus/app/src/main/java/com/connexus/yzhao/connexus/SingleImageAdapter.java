package com.connexus.yzhao.connexus;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.GridView;
import android.widget.ImageView;

import com.loopj.android.http.AsyncHttpClient;
import com.loopj.android.http.AsyncHttpResponseHandler;

import org.apache.http.Header;

/**
 * Created by wenxiao on 11/8/14.
 */
public class SingleImageAdapter extends BaseAdapter {

    private String[] Imgs;
    private Context mContext;
    private final AsyncHttpClient httpClient = new AsyncHttpClient();
    public static String STREAM_URL = "http://phase2connexus.appspot.com/androidViewSingleStream";
    private String imgPos;

    public SingleImageAdapter(Context c, String[] pics, String strPos) {
        mContext = c;
        Imgs = pics;
        imgPos = strPos;
    }

    @Override
    public int getCount() {
        return 16;
    }

    @Override
    public Object getItem(int position) {
        return Imgs[position];
    }

    @Override
    public long getItemId(int position) {
        //return position;
        return 0;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
        final ImageView imageView;
        final int pos = position;
        if (convertView == null) {
            imageView = new ImageView(mContext);
            imageView.setLayoutParams(new GridView.LayoutParams(60, 60));
            imageView.setScaleType(ImageView.ScaleType.CENTER_CROP);
            imageView.setPadding(4, 4, 4, 4);
        } else {
            imageView = (ImageView) convertView;
        }

        httpClient.get(STREAM_URL + "?strName=" + imgPos + "&pos=" + position, new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int statusCode, Header[] headers, byte[] response) {
                Imgs[pos] = new String(response);
                Bitmap bmp = BitmapFactory.decodeByteArray(response, 0, response.length);
                imageView.setImageBitmap(bmp);
            }

            @Override
            public void onFailure(int statusCode, Header[] headers, byte[] errorResponse, Throwable e) {
                System.out.println("Fail to get image on viewSingleStream page");
            }
        });

        return imageView;
    }

}
