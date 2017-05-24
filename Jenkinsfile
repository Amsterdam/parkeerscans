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

    stage("Test") {
        tryStep "Test", {
            sh "./jenkins-test.sh"
	}, {
            sh "docker-compose -p test -f docker-compose-test.yml down"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_kibana:${env.BUILD_NUMBER}", "kibana")
            image.push()
            image.push("acceptance")

	    def logstash = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_logstash:${env.BUILD_NUMBER}", "logstash")
            logstash.push()
            logstash.push("acceptance")

            def csvimporter = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_csvpgvoer:${env.BUILD_NUMBER}", "csvimporter")
            csvimporter.push()
            csvimporter.push("acceptance")

            def ppapi = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}", "api")
            ppapi.push()
            ppapi.push("acceptance")
        }
    }


String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}")
                image.pull()
                image.push("acceptance")
            }
        }
    }
    stage("Deploy to ACC") {
        tryStep "deployment", {
            build job: 'Subtask_Openstack_Playbook',
                    parameters: [
                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-predictive-parking.yml'],
                    ]
        }
    }
}
}
