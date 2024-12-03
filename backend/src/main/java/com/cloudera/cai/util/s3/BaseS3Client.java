/*******************************************************************************
 * CLOUDERA APPLIED MACHINE LEARNING PROTOTYPE (AMP)
 * (C) Cloudera, Inc. 2024
 * All rights reserved.
 *
 * Applicable Open Source License: Apache 2.0
 *
 * NOTE: Cloudera open source products are modular software products
 * made up of hundreds of individual components, each of which was
 * individually copyrighted.  Each Cloudera open source product is a
 * collective work under U.S. Copyright Law. Your license to use the
 * collective work is as provided in your written agreement with
 * Cloudera.  Used apart from the collective work, this file is
 * licensed for your use pursuant to the open source license
 * identified above.
 *
 * This code is provided to you pursuant a written agreement with
 * (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
 * this code. If you do not have a written agreement with Cloudera nor
 * with an authorized and properly licensed third party, you do not
 * have any rights to access nor to use this code.
 *
 * Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
 * contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
 * KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
 * WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
 * IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
 * AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
 * ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
 * OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
 * CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
 * RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
 * BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
 * DATA.
 ******************************************************************************/

package com.cloudera.cai.util.s3;

import static com.cloudera.cai.util.s3.CommonUtils.*;

import java.util.concurrent.atomic.AtomicInteger;
import lombok.extern.slf4j.Slf4j;

// BaseS3Client provides a wrapper to the underlying S3 object. The goal is to ensure that the
// S3 client object is
// _always_ valid when performing operations. If it is not, then that's a bug. This simplifies the
// handling of the API
// calls so that we don't have to keep worrying about refreshing the credentials on every call.
// We use a reference counter to keep track of when we have to shutdown a previous client that
// should not be used anymore.
@Slf4j
public class BaseS3Client {
  private final String bucketName;
  private final S3Config s3Config;

  private volatile AtomicInteger referenceCounter;

  public BaseS3Client(S3Config s3Config) {
    this.s3Config = s3Config;
    String s3AccessKey = s3Config.getAccessKey();
    String s3SecretKey = s3Config.getSecretKey();
    String s3Region = s3Config.getS3Region(); // FIXME(rch)
    this.bucketName = s3Config.getBucketName();

    // Start the counter with one because this class has a reference to it
    referenceCounter = new AtomicInteger(1);
  }

  private static boolean overrideUrlIsSet(S3Config s3Config) {
    return s3Config.getEndpointUrl() != null && !s3Config.getEndpointUrl().isEmpty();
  }
}
