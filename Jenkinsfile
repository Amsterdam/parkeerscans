#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage("Checkout") {
        checkout scm
    }

    stage("Build develop image") {
            tryStep "build", {
                def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}")
                image.push()
                image.push("acceptance")
            }
        }
}
