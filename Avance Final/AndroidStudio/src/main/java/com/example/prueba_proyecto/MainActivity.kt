package com.example.prueba_proyecto

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnEmpezar: Button = findViewById(R.id.btnEmpezar)
        btnEmpezar.setOnClickListener {
            val intent = Intent(this, MonitorActivity::class.java)
            startActivity(intent)
        }
    }
}

