package com.backend.tier_tok;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class TierTokApplication {

	public static void main(String[] args) {
		SpringApplication.run(TierTokApplication.class, args);
	}

}
